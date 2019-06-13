# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import copy
import logging
import os
import requests
import tempfile
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

try:
    from pretty_bad_protocol import gnupg
except ImportError as err:
    logging.getLogger(__name__).debug(err)

import odoo
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from ..controllers.main import BackupCloudStorage, BackupController, BACKUP_SERVICE_ENDPOINT

config_parser = ConfigParser.ConfigParser()
_logger = logging.getLogger(__name__)

REMOTE_STORAGE_DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
BACKUP_NAME_SUFFIX = ".zip"
BACKUP_NAME_ENCRYPT_SUFFIX = BACKUP_NAME_SUFFIX + ".enc"


class BackupConfig(models.Model):
    _name = 'odoo_backup_sh.config'
    _description = 'Backup Configurations'
    _rec_name = 'database'

    DATABASE_NAMES = [(db, db) for db in odoo.service.db.list_dbs() if db != 'session_store']
    ROTATION_OPTIONS = [('unlimited', 'Unlimited'), ('limited', 'Limited'), ('disabled', 'Disabled')]

    active = fields.Boolean('Active', compute='_compute_active', inverse='_inverse_active', store=True)
    database = fields.Selection(selection=DATABASE_NAMES, string='Database', required=True, copy=False)
    encrypt_backups = fields.Boolean(string="Encrypt Backups")
    encryption_password = fields.Char(string='Encryption Password')
    config_cron_ids = fields.One2many('odoo_backup_sh.config.cron', 'backup_config_id', string='Scheduled Auto Backups')
    hourly_rotation = fields.Selection(selection=ROTATION_OPTIONS, string='Hourly', default='unlimited')
    daily_rotation = fields.Selection(selection=ROTATION_OPTIONS, string='Daily', default='unlimited')
    weekly_rotation = fields.Selection(selection=ROTATION_OPTIONS, string='Weekly', default='unlimited')
    monthly_rotation = fields.Selection(selection=ROTATION_OPTIONS, string='Monthly', default='unlimited')
    yearly_rotation = fields.Selection(selection=ROTATION_OPTIONS, string='Yearly', default='unlimited')
    hourly_limit = fields.Integer('Hourly limit', default=1, help='How many hourly backups to preserve.')
    daily_limit = fields.Integer('Daily limit', default=1, help='How many daily backups to preserve.')
    weekly_limit = fields.Integer('Weekly limit', default=1, help='How many weekly backups to preserve.')
    monthly_limit = fields.Integer('Monthly limit', default=1, help='How many monthly backups to preserve.')
    yearly_limit = fields.Integer('Yearly limit', default=1, help='How many yearly backups to preserve.')
    storage_service = fields.Selection(selection=[('odoo_backup_sh', 'Odoo Backup sh')], default='odoo_backup_sh', required=True)
    unlimited_time_frame = fields.Char(default="hour")
    common_rotation = fields.Selection(selection=ROTATION_OPTIONS, default='unlimited')
    max_backups = fields.Integer(readonly=True, compute=lambda self: 0)
    backup_simulation = fields.Boolean(string="Demo Backup Simulation", default=False)

    _sql_constraints = [
        ('database_unique', 'unique (database, storage_service)', "Settings for this database already exist!"),
        ('hourly_limit_positive', 'check (hourly_limit > 0)', 'The hourly limit must be positive!'),
        ('daily_limit_positive', 'check (daily_limit > 0)', 'The daily limit must be positive!'),
        ('weekly_limit_positive', 'check (weekly_limit > 0)', 'The weekly limit must be positive!'),
        ('monthly_limit_positive', 'check (monthly_limit > 0)', 'The monthly limit must be positive!'),
        ('yearly_limit_positive', 'check (yearly_limit > 0)', 'The yearly limit must be positive!'),
    ]

    @api.onchange('config_cron_ids', 'hourly_rotation', 'daily_rotation', 'weekly_rotation', 'monthly_rotation', 'yearly_rotation')
    def _onchange_common_rotation(self):
        if self.config_cron_ids:
            rotation_list = [self.hourly_rotation, self.daily_rotation, self.weekly_rotation, self.monthly_rotation, self.yearly_rotation]
            if 'unlimited' in rotation_list:
                self.common_rotation = 'unlimited'
            elif 'unlimited' not in rotation_list and 'disabled' not in rotation_list:
                self.common_rotation = 'limited'
            elif 'unlimited' not in rotation_list and 'limited' not in rotation_list:
                self.common_rotation = 'disabled'
            else:
                self.common_rotation = 'limited'
            self.set_unlimited_time_frame()
        else:
            self.common_rotation = None

    def set_unlimited_time_frame(self):
        if self.hourly_rotation == 'unlimited':
            self.unlimited_time_frame = "hour"
        elif self.daily_rotation == 'unlimited':
            self.unlimited_time_frame = "day"
        elif self.weekly_rotation == 'unlimited':
            self.unlimited_time_frame = "week"
        elif self.monthly_rotation == 'unlimited':
            self.unlimited_time_frame = "month"
        elif self.yearly_rotation == 'unlimited':
            self.unlimited_time_frame = "year"
        else:
            self.unlimited_time_frame = None

    @api.onchange('common_rotation', 'hourly_limit', 'daily_limit', 'weekly_limit', 'monthly_limit', 'yearly_limit')
    def _onchange_max_backups(self):
        if self.common_rotation == 'limited':
            max_backups = 0
            if self.hourly_rotation == 'limited':
                max_backups += self.hourly_limit
            if self.daily_rotation == 'limited':
                max_backups += self.daily_limit
            if self.weekly_rotation == 'limited':
                max_backups += self.weekly_limit
            if self.monthly_rotation == 'limited':
                max_backups += self.monthly_limit
            if self.yearly_rotation == 'limited':
                max_backups += self.yearly_limit
            self.max_backups = max_backups

    @api.depends('config_cron_ids', 'config_cron_ids.ir_cron_id.active')
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
    def write(self, vals):
        if vals.get('common_rotation') == 'disabled':
            raise UserError(_("You cannot save the settings where all rotation options are disabled."))
        return super(BackupConfig, self).write(vals)

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

    def compute_auto_rotation_backup_dts(self, backup_dts, hourly=0, daily=0, weekly=0, monthly=0, yearly=0):
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
    def get_backup_list(self, cloud_params):
        try:
            return BackupCloudStorage.get_backup_list(cloud_params)
        except Exception as e:
            _logger.exception('Failed to load backups')
            raise UserError(_("Failed to load backups: %s") % e)

    @api.model
    def get_info_file_object(self, cloud_params, info_file_name, storage_service):
        if storage_service == 'odoo_backup_sh':
            return BackupCloudStorage.get_object(cloud_params, info_file_name)

    @api.model
    def create_info_file(self, info_file_object, storage_service):
        if storage_service == 'odoo_backup_sh':
            info_file = tempfile.NamedTemporaryFile()
            info_file.write(info_file_object['Body'].read())
            info_file.seek(0)
            return info_file

    @api.model
    def delete_remote_objects(self, cloud_params, remote_objects):
        odoo_backup_sh_objects = []
        for file in remote_objects:
            odoo_backup_sh_objects += [{'Key': '%s/%s' % (cloud_params['odoo_oauth_uid'], file[0])}]
        if odoo_backup_sh_objects:
            return BackupCloudStorage.delete_objects(cloud_params, odoo_backup_sh_objects)
        return {}

    @api.model
    def update_info(self, cloud_params):
        # FIXME: We need to get ('backup.name', 'backup.service')
        backup_list = self.get_backup_list(cloud_params)
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
            for file in backup_list['backup_list']:
                file_name = file[0]
                service_name = file[1]
                file_name_parts = file_name.split('.')
                backup_dt_part_index = -3 if file_name_parts[-1] == 'enc' else -2
                db_name = '.'.join(file_name_parts[:backup_dt_part_index])
                backup_dt = datetime.strptime(file_name_parts[backup_dt_part_index], REMOTE_STORAGE_DATETIME_FORMAT)
                if db_name not in remote_backups:
                    remote_backups[db_name] = {}
                if backup_dt not in remote_backups[db_name]:
                    remote_backups[db_name][backup_dt] = []
                remote_backups[db_name][backup_dt].append((file_name, service_name))

            # Compute remote backup objects to delete according to auto rotation parameters.
            remote_objects_to_delete = []
            for backup_config in self.search([('active', '=', True)]):
                limits = {}
                for time_frame in ('hourly', 'daily', 'weekly', 'monthly', 'yearly'):
                    limit_option = getattr(backup_config, time_frame + '_rotation')
                    if limit_option == 'limited':
                        limits[time_frame] = getattr(backup_config, time_frame + '_limit')
                    elif limit_option == 'unlimited':
                        limits[time_frame] = 1000000
                if limits:
                    remote_db = remote_backups.get(backup_config.database, False)
                    if not remote_db:
                        continue
                    backup_dts = copy.deepcopy(remote_db)
                    needed_backup_dts = self.compute_auto_rotation_backup_dts(backup_dts, **limits)
                    for backup_dt in backup_dts:
                        if backup_dt not in needed_backup_dts:
                            remote_objects_to_delete += [file in remote_backups[backup_config.database][backup_dt]]
                            del remote_backups[backup_config.database][backup_dt]

            # Delete unnecessary remote backup objects
            if remote_objects_to_delete:
                res = self.delete_remote_objects(cloud_params, remote_objects_to_delete)
                if res and 'reload_page' in res:
                    return res

            # Delete unnecessary local backup info records
            backup_info_ids_to_delete = [
                r.id for r in self.env['odoo_backup_sh.backup_info'].search([]) if
                (r.database not in remote_backups or r.upload_datetime not in remote_backups[r.database])
            ]
            self.env['odoo_backup_sh.backup_info'].browse(backup_info_ids_to_delete).unlink()

            # Create missing local backup info records
            for db_name, backup_dts in remote_backups.items():
                for backup_dt, files in backup_dts.items():
                    if not self.env['odoo_backup_sh.backup_info'].search([
                        ('database', '=', db_name),
                        ('upload_datetime', '>=', datetime.strftime(backup_dt, DEFAULT_SERVER_DATETIME_FORMAT)),
                        ('upload_datetime', '<', datetime.strftime(backup_dt + relativedelta(seconds=1),
                                                                   DEFAULT_SERVER_DATETIME_FORMAT))
                    ]):
                        info_file = files[0] if files[0][0][-5:] == '.info' else files[1] if len(files) == 2 else False
                        if not info_file:
                            continue
                        info_file_name = info_file[0]
                        info_file_service = info_file[1]
                        info_file_object = self.get_info_file_object(cloud_params, info_file_name, info_file_service)

                        if 'reload_page' in info_file_object:
                            return info_file_object
                        info_file = self.create_info_file(info_file_object, info_file_service)
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
    def get_dump_stream_and_info_file(self, name, service, ts):
        dump_stream = odoo.service.db.dump_db(name, None, 'zip')
        config_record = self.with_context({'active_test': False}).search([('database', '=', name),
                                                                          ('storage_service', '=', service)])
        if config_record.encrypt_backups:
            # GnuPG ignores the --output parameter with an existing file object as value
            backup_encrpyted = tempfile.NamedTemporaryFile()
            backup_encrpyted_name = backup_encrpyted.name
            os.unlink(backup_encrpyted_name)
            gnupg.GPG().encrypt(dump_stream, symmetric=True, passphrase=config_record.encryption_password,
                                encrypt=False, output=backup_encrpyted_name)
            dump_stream = open(backup_encrpyted_name, 'rb')
        backup_size = dump_stream.seek(0, 2) / 1024 / 1024
        dump_stream.seek(0)
        info_file = tempfile.TemporaryFile()
        info_file.write('[common]\n'.encode())
        info_file_content = {
            'database': name,
            'encrypted': True if config_record.encrypt_backups else False,
            'upload_datetime': ts,
            'backup_size': backup_size,
            'storage_service': config_record.storage_service
        }
        for key, value in info_file_content.items():
            line = key + ' = ' + str(value) + '\n'
            info_file.write(line.encode())
        info_file.seek(0)
        return dump_stream, info_file, info_file_content

    @api.model
    def make_backup(self, name, service, init_by_cron_id=None):
        if init_by_cron_id and not self.env['ir.cron'].browse(init_by_cron_id).active:
            # The case when an auto backup was initiated by an inactive backup config.
            return None
        dt = datetime.utcnow()
        ts = dt.strftime(REMOTE_STORAGE_DATETIME_FORMAT)
        dump_stream, info_file, info_file_content = self.get_dump_stream_and_info_file(name, service, ts)
        dump_stream.seek(0)
        info_file.seek(0)
        cloud_params = BackupController.get_cloud_params()
        s3_backup_path = '%s/%s.%s%s' % (cloud_params['odoo_oauth_uid'], name, ts,
                                         BACKUP_NAME_ENCRYPT_SUFFIX if info_file_content.get('encrypted') else BACKUP_NAME_SUFFIX)
        s3_info_file_path = '%s/%s.%s.info' % (cloud_params['odoo_oauth_uid'], name, ts)
        # Upload two backup objects to AWS S3
        for obj, obj_path in [[dump_stream, s3_backup_path], [info_file, s3_info_file_path]]:
            try:
                res = BackupCloudStorage.put_object(cloud_params, obj, obj_path)
                if res and 'reload_page' in res:
                    return res
            except Exception as e:
                _logger.exception('Failed to load backups')
                raise UserError(_("Failed to load backups: %s") % e)
        # Create new record with backup info data
        info_file_content['upload_datetime'] = dt
        self.env['odoo_backup_sh.backup_info'].create(info_file_content)
        if init_by_cron_id:
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
        config = self.env['odoo_backup_sh.config'].browse(vals['backup_config_id'])
        vals.update({
            'name': 'Odoo-backup.sh: Backup the "%s" database and send it to the remote storage' % config.database,
            'model_id': self.env.ref('odoo_backup_sh.model_odoo_backup_sh_config').id,
            'state': 'code',
            'numbercall': -1,
            'doall': False,
        })
        res = super(BackupConfigCron, self).create(vals)
        res.write({
            'code': 'model.make_backup("%s", "%s", init_by_cron_id=%s)' % (config.database, config.storage_service, res.ir_cron_id.id),
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
    _rec_name = 'database'

    database = fields.Char(string='Database Name', readonly=True)
    upload_datetime = fields.Datetime(string='Upload Datetime', readonly=True)
    encrypted = fields.Boolean(string='Encrypted', readonly=True)
    backup_size = fields.Float(string='Backup Size, MB', readonly=True)
    storage_service = fields.Selection(selection=[('odoo_backup_sh', 'Odoo Backup sh')], readonly=True)

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


class BackupNotification(models.Model):
    _name = 'odoo_backup_sh.notification'
    _description = 'Backup Notifications'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_create desc'
    _rec_name = 'date_create'

    date_create = fields.Datetime('Date', readonly=True, default=fields.Datetime.now)
    type = fields.Selection([
        ('insufficient_credits', 'Insufficient Credits'),
        ('forecast_insufficient_credits', 'Forecast About Insufficient Credits'),
        ('other', 'Other')
    ], string='Notification Type', readonly=True, default='other')
    message = fields.Text('Message', readonly=True)
    is_read = fields.Boolean('Is Read', readonly=True)

    @api.multi
    def toggle_is_read(self):
        self.write({'is_read': not self.is_read})
        self.activity_ids.unlink()
        return True

    @api.multi
    def create_mail_activity_record(self):
        self.env['mail.activity'].create({
            'res_id': self.id,
            'res_model_id': self.env.ref('odoo_backup_sh.model_odoo_backup_sh_notification').id,
            'activity_type_id': self.env.ref('odoo_backup_sh.mail_activity_data_notification').id,
            'summary': 'Please read important message.',
            'date_deadline': datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
        })

    @api.model
    def fetch_notifications(self):
        config_params = self.env['ir.config_parameter']
        data = {'params': {
            'user_key': BackupController.get_config_values(
                'options', ['odoo_backup_user_key'])['odoo_backup_user_key'],
            'date_last_request': config_params.get_param('odoo_backup_sh.date_last_request', None)
        }}
        response = requests.post(BACKUP_SERVICE_ENDPOINT + '/fetch_notifications', json=data).json()['result']
        config_params.set_param('odoo_backup_sh.date_last_request', response['date_last_request'])
        for n in response['notifications']:
            if n.get('type') == 'forecast_insufficient_credits':
                existing_forecast_msg = self.search([('type', '=', 'forecast_insufficient_credits')])
                if existing_forecast_msg:
                    if existing_forecast_msg.activity_ids:
                        existing_forecast_msg.activity_ids.unlink()
                    existing_forecast_msg.unlink()
            new_record = self.create(n)
            new_record.create_mail_activity_record()


class BackupRemoteStorage(models.Model):
    _name = 'odoo_backup_sh.remote_storage'
    _description = 'Remote Storage Usage'

    date = fields.Date(string='Date of Update', readonly=True)
    total_used_remote_storage = fields.Integer(string='Total Usage, MB', readonly=True)
    s3_used_remote_storage = fields.Integer(string='Odoo Backup sh Usage, MB', readonly=True)

    @api.multi
    def compute_total_used_remote_storage(self):
        self.compute_s3_used_remote_storage()
        amount = sum(self.env['odoo_backup_sh.backup_info'].search([]).mapped('backup_size'))
        today_record = self.search([('date', '=', datetime.strftime(datetime.now(), DEFAULT_SERVER_DATE_FORMAT))])
        if today_record:
            today_record.total_used_remote_storage = amount
        else:
            self.create({
                'date': datetime.now(),
                'total_used_remote_storage': amount
            })

    @api.multi
    def compute_s3_used_remote_storage(self):
        amount = sum(self.env['odoo_backup_sh.backup_info'].search([('storage_service', '=', 'odoo_backup_sh')]).mapped('backup_size'))
        today_record = self.search([('date', '=', datetime.strftime(datetime.now(), DEFAULT_SERVER_DATE_FORMAT))])
        if today_record:
            today_record.s3_used_remote_storage = amount
        else:
            self.create({
                'date': datetime.now(),
                's3_used_remote_storage': amount
            })


class DeleteRemoteBackupWizard(models.TransientModel):
    _name = "odoo_backup_sh.delete_remote_backup_wizard"
    _description = "Delete Remote Backups Wizard"

    @api.multi
    def delete_remove_backup_button(self):
        record_ids = (self._context.get('active_model') == 'odoo_backup_sh.backup_info' and
                      self._context.get('active_ids') or [])
        backup_info_records = self.env['odoo_backup_sh.backup_info'].search([('id', 'in', record_ids)])
        cloud_params = BackupController.get_cloud_params()
        remote_objects_to_delete = []
        backup_s3_info_records = backup_info_records.filtered(lambda r: r.storage_service == 'odoo_backup_sh')

        for record in backup_s3_info_records:
            backup_files_suffixes = ['.zip', '.info']
            if record.encrypted:
                backup_files_suffixes[0] += '.enc'
            upload_datetime = datetime.strftime(record.upload_datetime, REMOTE_STORAGE_DATETIME_FORMAT)
            for suffix in backup_files_suffixes:
                remote_objects_to_delete += [{
                    'Key': '%s/%s.%s%s' % (cloud_params['odoo_oauth_uid'], record.database, upload_datetime, suffix)
                }]
        # Delete unnecessary remote backup objects
        if remote_objects_to_delete:
            res = BackupCloudStorage.delete_objects(cloud_params, remote_objects_to_delete)
            if res and 'reload_page' in res:
                raise UserError(_("Something went wrong. Please update backup dashboard page."))
        backup_s3_info_records.unlink()
