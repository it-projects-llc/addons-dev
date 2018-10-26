# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import copy
import logging
import os
import tempfile
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

try:
    import boto3
    import botocore
    from pretty_bad_protocol import gnupg
except ImportError as err:
    logging.getLogger(__name__).debug(err)

import odoo
from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from ..controllers.main import BackupController

_logger = logging.getLogger(__name__)

REMOTE_STORAGE_DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"


class BackupConfig(models.Model):
    _name = 'odoo_backup_sh.config'
    _description = 'Backup Configurations'

    DATABASE_NAMES = [(db, db) for db in odoo.service.db.list_dbs() if db != 'session_store']

    active = fields.Boolean('Active', compute='_compute_active', inverse='_inverse_active', store=True)
    database = fields.Selection(selection=DATABASE_NAMES, string='Database', required=True, copy=False)
    config_cron_ids = fields.One2many('odoo_backup_sh.config.cron', 'backup_config_id', string='Scheduled Auto Backups')
    hourly = fields.Integer(
        'Hourly', default=-1, help='How many hourly backups to preserve, a negative number indicates no limit.')
    daily = fields.Integer(
        'Daily', default=-1, help='How many daily backups to preserve, a negative number indicates no limit.')
    weekly = fields.Integer(
        'Weekly', default=-1, help='How many weekly backups to preserve, a negative number indicates no limit.')
    monthly = fields.Integer(
        'Monthly', default=-1, help='How many monthly backups to preserve, a negative number indicates no limit.')
    yearly = fields.Integer(
        'Yearly', default=-1, help='How many yearly backups to preserve, a negative number indicates no limit.')

    _sql_constraints = [
        ('database_unique', 'unique (database)', "Settings for this database already exist!"),
    ]

    @api.depends('config_cron_ids', 'config_cron_ids.active')
    @api.multi
    def _compute_active(self):
        for backup_config in self:
            backup_config.active = backup_config.config_cron_ids and any(backup_config.config_cron_ids.mapped('active'))

    @api.multi
    def _inverse_active(self):
        for backup_config in self:
            backup_config.config_cron_ids.write({
                'active': backup_config.active
            })

    @api.multi
    def unlink(self):
        self.mapped('config_cron_ids').unlink()
        return super(BackupConfig, self).unlink()

    @api.model
    def action_dashboard_redirect(self):
        return self.env.ref('odoo_backup_sh.backup_dashboard').read()[0]

    @api.model
    def get_cloud_params(self, redirect):
        return BackupController.get_cloud_params(redirect)

    @api.model
    def check_insufficient_credit(self, credit):
        return BackupController.check_insufficient_credit(credit)

    def compute_auto_rotation_backup_dts(self, backup_dts, hourly=-1, daily=-1, weekly=-1, monthly=-1, yearly=-1):
        backup_dts = sorted(copy.deepcopy(backup_dts), reverse=True)
        last_backup_dt = backup_dts.pop(0)
        # We always take the last backup and based on its upload time we compute time frames
        # for other backups.
        needed_backup_dts = [last_backup_dt]
        if hourly > 1:
            last_backup_dt_of_hour = last_backup_dt
            for hour in range(hourly-1):
                next_max_dt_edge = last_backup_dt_of_hour.replace(minute=0, second=0)
                for dt in backup_dts:
                    if dt < next_max_dt_edge:
                        needed_backup_dts.append(dt)
                        last_backup_dt_of_hour = dt
                        break
        if daily > 1:
            last_backup_dt_of_day = last_backup_dt
            for day in range(daily-1):
                next_max_dt_edge = last_backup_dt_of_day.replace(hour=0, minute=0, second=0)
                for dt in backup_dts:
                    if dt < next_max_dt_edge:
                        if dt not in needed_backup_dts:
                            needed_backup_dts.append(dt)
                        last_backup_dt_of_day = dt
                        break
        if weekly > 1:
            last_backup_dt_of_week = last_backup_dt
            for week in range(weekly-1):
                last_backup_dt_day = last_backup_dt_of_week.replace(hour=0, minute=0, second=0)
                next_max_dt_edge = last_backup_dt_day - timedelta(days=last_backup_dt_day.weekday())
                for dt in backup_dts:
                    if dt < next_max_dt_edge:
                        if dt not in needed_backup_dts:
                            needed_backup_dts.append(dt)
                        last_backup_dt_of_week = dt
                        break
        if monthly > 1:
            last_backup_dt_of_month = last_backup_dt
            for month in range(monthly-1):
                next_max_dt_edge = last_backup_dt_of_month.replace(day=1, hour=0, minute=0, second=0)
                for dt in backup_dts:
                    if dt < next_max_dt_edge:
                        if dt not in needed_backup_dts:
                            needed_backup_dts.append(dt)
                        last_backup_dt_of_month = dt
                        break
        if yearly > 1:
            last_backup_dt_of_year = last_backup_dt
            for year in range(yearly-1):
                next_max_dt_edge = last_backup_dt_of_year.replace(month=1, day=1, hour=0, minute=0, second=0)
                for dt in backup_dts:
                    if dt < next_max_dt_edge:
                        if dt not in needed_backup_dts:
                            needed_backup_dts.append(dt)
                        last_backup_dt_of_year = dt
                        break
        return needed_backup_dts

    @api.model
    def update_info(self, cloud_params):
        backup_list = BackupController.load_backup_list(cloud_params)
        if 'backup_list' in backup_list:
            # Create a dictionary with remote backup objects:
            # remote_backups = {
            #     db_name: {
            #         backup_datetime(datetime.datetime): [backup_file_name(str), info_file_name(str)],
            #         ...
            #     },
            #     ...
            # }
            remote_backups = {}
            for file_name in backup_list['backup_list']:
                file_name_parts = file_name.split('.')
                backup_dt_part_index = -3 if file_name_parts[-1] == 'enc' else -2
                db_name = '.'.join(file_name_parts[:backup_dt_part_index])
                backup_dt = datetime.strptime(file_name_parts[backup_dt_part_index], REMOTE_STORAGE_DATETIME_FORMAT)
                if db_name not in remote_backups:
                    remote_backups[db_name] = {}
                if backup_dt not in remote_backups[db_name]:
                    remote_backups[db_name][backup_dt] = []
                remote_backups[db_name][backup_dt].append(file_name)

            # Compute remote backup objects to delete according to auto rotation parameters.
            remote_objects_to_delete = []
            for backup_config in self.search([('active', '=', True)]):
                if (backup_config.hourly > 0 or backup_config.daily > 0 or backup_config.weekly > 0 or
                        backup_config.monthly > 0 or backup_config.yearly > 0):
                    backup_dts = copy.deepcopy(remote_backups[backup_config.database])
                    needed_backup_dts = self.compute_auto_rotation_backup_dts(
                        backup_dts, backup_config.hourly, backup_config.daily,
                        backup_config.weekly, backup_config.monthly, backup_config.yearly)
                    for backup_dt in backup_dts:
                        if backup_dt not in needed_backup_dts:
                            remote_objects_to_delete += [
                                {'Key': '%s/%s' % (cloud_params['odoo_oauth_uid'], file_name)} for file_name in
                                remote_backups[backup_config.database][backup_dt]
                            ]
                            del remote_backups[backup_config.database][backup_dt]

            s3_client = boto3.client('s3', aws_access_key_id=cloud_params['amazon_access_key'],
                                     aws_secret_access_key=cloud_params['amazon_secret_access_key'])

            # Delete unnecessary remote backup objects
            if remote_objects_to_delete:
                try:
                    s3_client.delete_objects(
                        Bucket=cloud_params['amazon_bucket_name'], Delete={'Objects': remote_objects_to_delete})
                    objects_names = [obj['Key'] for obj in remote_objects_to_delete]
                    _logger.info('Following backup objects have been deleted from the remote storage: %s',
                                 ', '.join(objects_names))
                except botocore.exceptions.ClientError as e:
                    raise exceptions.ValidationError(_("Amazon error: ") + e.response['Error']['Message'])

            # Delete unnecessary local backup info records
            backup_info_ids_to_delete = [
                r.id for r in self.env['odoo_backup_sh.backup_info'].search([]) if
                (r.database not in remote_backups or
                 datetime.strptime(r.upload_datetime, DEFAULT_SERVER_DATETIME_FORMAT) not in remote_backups[r.database])
            ]
            self.env['odoo_backup_sh.backup_info'].browse(backup_info_ids_to_delete).unlink()

            # Create missing local backup info records
            for db_name, backup_dts in remote_backups.items():
                for backup_dt, files_names in backup_dts.items():
                    if not self.env['odoo_backup_sh.backup_info'].search([
                        ('database', '=', db_name),
                        ('upload_datetime', '>=', datetime.strftime(backup_dt, DEFAULT_SERVER_DATETIME_FORMAT)),
                        ('upload_datetime', '<', datetime.strftime(backup_dt + relativedelta(seconds=1),
                                                                   DEFAULT_SERVER_DATETIME_FORMAT))
                    ]):
                        info_file_name = files_names[0] if files_names[0][-5:] == '.info' else files_names[1]
                        try:
                            info_file_object = s3_client.get_object(
                                Bucket=cloud_params['amazon_bucket_name'],
                                Key='%s/%s' % (cloud_params['odoo_oauth_uid'], info_file_name)
                            )
                        except botocore.exceptions.ClientError as e:
                            raise exceptions.ValidationError(_("Amazon error: ") + e.response['Error']['Message'])
                        info_file = tempfile.NamedTemporaryFile()
                        info_file.write(info_file_object['Body'].read())
                        info_file.seek(0)
                        config_parser = ConfigParser.RawConfigParser()
                        config_parser.read(info_file.name)
                        backup_info_vals = {}
                        for (name, value) in config_parser.items('common'):
                            if value == 'True' or value == 'true':
                                value = True
                            if value == 'False' or value == 'false':
                                value = False
                            if name == 'upload_datetime':
                                value = datetime.strptime(value, REMOTE_STORAGE_DATETIME_FORMAT)
                            elif name == 'backup_size':
                                value = int(float(value))
                            backup_info_vals[name] = value
                        self.env['odoo_backup_sh.backup_info'].create(backup_info_vals)
        return backup_list

    @api.model
    def make_backup(self, name, init_by_cron_id=None):
        if init_by_cron_id and not self.env['ir.cron'].browse(init_by_cron_id).active:
            # The case when an auto backup was initiated by an inactive backup config.
            return None
        dump_stream = odoo.service.db.dump_db(name, None, 'zip')
        backup_name_suffix = '.zip'
        if self.env['ir.config_parameter'].get_param('odoo_backup_sh.encrypt_backups', 'False').lower() == 'true':
            passphrase = config.get('odoo_backup_encryption_password')
            if not passphrase:
                raise UserError(_('Encryption password is not found. Please check your module settings.'))
            backup_name_suffix += '.enc'
            # GnuPG ignores the --output parameter with an existing file object as value
            backup_encrpyted = tempfile.NamedTemporaryFile()
            backup_encrpyted_name = backup_encrpyted.name
            os.unlink(backup_encrpyted_name)
            gnupg.GPG().encrypt(
                dump_stream, symmetric=True, passphrase=passphrase, encrypt=False, output=backup_encrpyted_name)
            dump_stream = open(backup_encrpyted_name, 'rb')
        backup_size = dump_stream.seek(0, 2) / 1024 / 1024
        dump_stream.seek(0)
        cloud_params = BackupController.get_cloud_params()
        dt = datetime.utcnow()
        ts = dt.strftime(REMOTE_STORAGE_DATETIME_FORMAT)
        s3_backup_path = '%s/%s.%s%s' % (cloud_params['odoo_oauth_uid'], name, ts, backup_name_suffix)
        info_file = tempfile.TemporaryFile()
        info_file.write('[common]\n'.encode())
        info_file_content = {
            'database': name,
            'encrypted': True if '.enc' in backup_name_suffix else False,
            'upload_datetime': ts,
            'backup_size': backup_size,
        }
        for key, value in info_file_content.items():
            line = key + ' = ' + str(value) + '\n'
            info_file.write(line.encode())
        info_file.seek(0)
        s3_info_file_path = '%s/%s.%s.info' % (cloud_params['odoo_oauth_uid'], name, ts)
        # Create new record with backup info data
        info_file_content['upload_datetime'] = dt
        self.env['odoo_backup_sh.backup_info'].create(info_file_content)
        # Upload two backup objects to AWS S3
        try:
            s3_client = boto3.client('s3', aws_access_key_id=cloud_params['amazon_access_key'],
                                     aws_secret_access_key=cloud_params['amazon_secret_access_key'])
            s3_client.put_object(Body=dump_stream, Bucket=cloud_params['amazon_bucket_name'], Key=s3_backup_path)
            s3_client.put_object(Body=info_file, Bucket=cloud_params['amazon_bucket_name'], Key=s3_info_file_path)
            _logger.info('Following backup objects have been put in a remote storage: %s',
                         ', '.join([s3_backup_path, s3_info_file_path]))
        except botocore.exceptions.ClientError as e:
            raise exceptions.ValidationError(_("Amazon error: ") + e.response['Error']['Message'])
        self.update_info(cloud_params)
        return None


class BackupConfigCron(models.Model):
    _name = 'odoo_backup_sh.config.cron'
    _inherits = {'ir.cron': 'ir_cron_id'}
    _description = 'Backup Configuration Scheduled Actions'

    backup_config_id = fields.Many2one(
        'odoo_backup_sh.config', string='Backup Configuration', required=True)
    ir_cron_id = fields.Many2one('ir.cron', string='Scheduled Action', required=True, ondelete='restrict')

    @api.model
    def create(self, vals):
        database = self.env['odoo_backup_sh.config'].browse(vals['backup_config_id']).database
        vals.update({
            'name': 'Odoo-backup.sh: Backup the "%s" database and send it to the remote storage' % database,
            'model_id': self.env.ref('odoo_backup_sh.model_odoo_backup_sh_config').id,
            'state': 'code',
            'numbercall': -1,
            'doall': False,
        })
        res = super(BackupConfigCron, self).create(vals)
        res.write({
            'code': 'model.make_backup("%s", init_by_cron_id=%s)' % (database, res.ir_cron_id.id),
        })
        return res

    @api.multi
    def unlink(self):
        ir_cron_ids = [r.ir_cron_id.id for r in self]
        res = super(BackupConfigCron, self).unlink()
        if ir_cron_ids:
            self.env['ir.cron'].browse(ir_cron_ids).unlink()
        return res


class BackupInfo(models.Model):
    _name = 'odoo_backup_sh.backup_info'
    _description = 'Information About Backups'

    database = fields.Char(string='Database Name', readonly=True)
    upload_datetime = fields.Datetime(string='Upload Datetime', readonly=True)
    encrypted = fields.Boolean(string='Encrypted', readonly=True)
    backup_size = fields.Integer(string='Backup Size, MB', readonly=True)

    @api.model
    def create(self, vals):
        res = super(BackupInfo, self).create(vals)
        self.env['odoo_backup_sh.remote_storage'].compute_total_used_remote_storage()
        return res

    @api.multi
    def unlink(self):
        res = super(BackupInfo, self).unlink()
        self.env['odoo_backup_sh.remote_storage'].compute_total_used_remote_storage()
        return res


class BackupRemoteStorage(models.Model):
    _name = 'odoo_backup_sh.remote_storage'
    _description = 'Remote Storage Usage'

    date = fields.Date(string='Date of Update', readonly=True)
    total_used_remote_storage = fields.Integer(string='Total Usage, MB', readonly=True)

    @api.multi
    def compute_total_used_remote_storage(self):
        amount = sum(self.env['odoo_backup_sh.backup_info'].search([]).mapped('backup_size'))
        today_record = self.search([('date', '=', datetime.strftime(datetime.now(), DEFAULT_SERVER_DATE_FORMAT))])
        if today_record:
            today_record.total_used_remote_storage = amount
        else:
            self.create({
                'date': datetime.now(),
                'total_used_remote_storage': amount
            })


class DeleteRemoteBackupWizard(models.TransientModel):
    _name = "odoo_backup_sh.delete_remote_backup_wizard"
    _description = "Delete Remote Backups Wizard"

    @api.multi
    def delete_remove_backup_button(self):
        record_ids = (self._context.get('active_model') == 'odoo_backup_sh.backup_info' and
                      self._context.get('active_ids') or [])
        backup_info_records = self.env['odoo_backup_sh.backup_info'].browse(record_ids)
        cloud_params = BackupController.get_cloud_params()
        remote_objects_to_delete = []
        for record in backup_info_records:
            backup_files_suffixes = ['.zip', '.info']
            if record.encrypted:
                backup_files_suffixes[0] += '.enc'
            upload_datetime = datetime.strftime(datetime.strptime(
                record.upload_datetime, DEFAULT_SERVER_DATETIME_FORMAT), REMOTE_STORAGE_DATETIME_FORMAT)
            for suffix in backup_files_suffixes:
                remote_objects_to_delete += [{
                    'Key': '%s/%s.%s%s' % (cloud_params['odoo_oauth_uid'], record.database, upload_datetime, suffix)
                }]
        # Delete unnecessary remote backup objects
        if remote_objects_to_delete:
            s3_client = boto3.client('s3', aws_access_key_id=cloud_params['amazon_access_key'],
                                     aws_secret_access_key=cloud_params['amazon_secret_access_key'])
            try:
                s3_client.delete_objects(
                    Bucket=cloud_params['amazon_bucket_name'], Delete={'Objects': remote_objects_to_delete})
                objects_names = [obj['Key'] for obj in remote_objects_to_delete]
                _logger.info('Following backup objects have been deleted from the remote storage: %s',
                             ', '.join(objects_names))
            except botocore.exceptions.ClientError as e:
                raise exceptions.ValidationError(_("Amazon error: ") + e.response['Error']['Message'])
        backup_info_records.unlink()
