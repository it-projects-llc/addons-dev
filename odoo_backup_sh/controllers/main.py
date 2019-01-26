# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import jinja2
import json
import logging
import os
import random
import requests
import string
import tempfile
from contextlib import closing
from datetime import datetime, timedelta

import odoo
from odoo import fields, http, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.service import db
from odoo.sql_db import db_connect
from odoo.tools import config, DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import str2bool
from odoo.addons import web
from odoo.addons.iap import jsonrpc, InsufficientCreditError
from odoo.addons.web.controllers.main import DBNAME_PATTERN

try:
    import boto3
    import botocore
    from pretty_bad_protocol import gnupg
except ImportError as err:
    logging.getLogger(__name__).debug(err)

try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser
config_parser = ConfigParser.ConfigParser()

path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
loader = jinja2.FileSystemLoader(path)
env = jinja2.Environment(loader=loader, autoescape=True)
BACKUP_SERVICE_ENDPOINT = 'http://odoo-backup.sh:8069'


class BackupDatabase(web.controllers.main.Database):

    def _render_template(self, **d):
        res = super(BackupDatabase, self)._render_template(**d)
        # Show button 'Restore via Odoo-backup.sh' on web/database/manager and web/database/selector pages
        place_for_backup_button = res.find(
            '<button type="button" data-toggle="modal" data-target=".o_database_restore"'
        )
        if place_for_backup_button == -1:
            place_for_backup_button = res.find(
                '<a role="button" data-toggle="modal" data-target=".o_database_restore" class="btn btn-link">'
            )
        if place_for_backup_button != -1:
            d['list_db'] = config['list_db']
            d['databases'] = []
            try:
                d['databases'] = http.db_list()
            except odoo.exceptions.AccessDenied:
                monodb = http.db_monodb()
                if monodb:
                    d['databases'] = [monodb]
            backup_button = env.get_template("backup_button.html").render(d)
            res = res[:place_for_backup_button] + backup_button + res[place_for_backup_button:]
        return res


class BackupController(http.Controller):

    @classmethod
    def get_cloud_params(cls, redirect=None):
        config_parser.read(config.rcfile)
        cloud_params = {}
        for name in ['odoo_backup_user_key', 'amazon_bucket_name', 'amazon_access_key', 'amazon_secret_access_key',
                     'odoo_oauth_uid']:
            cloud_params[name] = config_parser.get('options', name, fallback=None)
        if None in cloud_params.values() and redirect:
            cloud_params = cls.update_cloud_params(cloud_params, redirect)
        return cloud_params

    @classmethod
    def update_cloud_params(cls, cloud_params, redirect):
        user_key = cloud_params['odoo_backup_user_key']
        if not user_key:
            user_key = ''.join(random.choice(string.hexdigits) for _ in range(30))
            config_parser.set('options', 'odoo_backup_user_key', user_key)
            cls.write_config(config_parser)
        cloud_params = requests.get(
            BACKUP_SERVICE_ENDPOINT + '/get_cloud_params',
            params={'user_key': user_key, 'redirect': redirect}
        ).json()
        if 'auth_link' not in cloud_params:
            for param_key, param_value in cloud_params.items():
                config_parser.set('options', param_key, param_value)
            cls.write_config(config_parser)
            cloud_params['updated'] = True  # The mark that all params are updated
        return cloud_params

    @classmethod
    def load_backup_list(cls, cloud_params):
        try:
            s3_client = boto3.client('s3', aws_access_key_id=cloud_params['amazon_access_key'],
                                     aws_secret_access_key=cloud_params['amazon_secret_access_key'])
            user_dir_name = '%s/' % cloud_params['odoo_oauth_uid']
            s3_user_dir_info = s3_client.list_objects_v2(
                Bucket=cloud_params['amazon_bucket_name'], Prefix=user_dir_name, Delimiter='/')
        except botocore.exceptions.ClientError as e:
            if isinstance(e, dict):
                status_code = e['ResponseMetadata']['HTTPStatusCode']
            else:
                status_code = e.response['ResponseMetadata']['HTTPStatusCode']
            if status_code == 403 and not cloud_params.get('updated'):
                config_parser.read(config.rcfile)
                # Delete local cloud parameters and receive it again to make sure they are up-to-date.
                for key in ['amazon_bucket_name', 'amazon_access_key', 'amazon_secret_access_key', 'odoo_oauth_uid']:
                    config_parser.remove_option('options', key)
                cls.write_config(config_parser)
                return {'reload_page': True}
            else:
                return {'error': "Amazon Web Services error: %s" % e.response['Error']['Message']}
        backup_list = [
            obj['Key'][len(user_dir_name):] for obj in s3_user_dir_info.get('Contents', {}) if obj.get('Size')]
        return {'backup_list': backup_list}

    @classmethod
    def check_insufficient_credit(cls, credit):
        user_token = request.env['iap.account'].sudo().get('odoo_backup_sh')
        params = {
            'account_token': user_token.account_token,
            'cost': credit,
        }
        try:
            jsonrpc(BACKUP_SERVICE_ENDPOINT + '/make_backup', params=params)
        except InsufficientCreditError as e:
            error_data = json.loads(e.data['message'])
            credit_url = request.env['iap.account'].sudo().get_credits_url(
                error_data['base_url'], error_data['service_name'], error_data['credit'])
            return credit_url
        return None

    @classmethod
    def write_config(cls, config_parser_obj):
        with open(config.rcfile, 'w') as configfile:
            config_parser_obj.write(configfile)

    @http.route('/web/database/backups', type='http', auth="none")
    def backup_list(self):
        cloud_params = self.get_cloud_params(request.httprequest.url)
        if 'auth_link' in cloud_params:
            return "<html><head><script>window.location.href = '%s';</script></head></html>" % cloud_params['auth_link']
        backup_list = self.load_backup_list(cloud_params)
        if 'reload_page' in backup_list:
            return "<html><head><script>window.location.href = '%s';</script></head></html>" % request.httprequest.url
        backup_list_wo_info = [name for name in backup_list['backup_list'] if name[-5:] != '.info']
        page_values = {
            'backup_list': backup_list_wo_info,
            'error': backup_list.get('error'),
            'pattern': DBNAME_PATTERN,
            'insecure': odoo.tools.config.verify_admin_password('admin')
        }
        return env.get_template("backup_list.html").render(page_values)

    @http.route('/web/database/restore_via_odoo_backup_sh', type='http', auth="none", methods=['POST'], csrf=False)
    def restore_via_odoo_backup_sh(self, master_pwd, backup_file_name, name, copy=False):
        cloud_params = self.get_cloud_params(request.httprequest.url)
        backup_object = request.env['odoo_backup_sh.cloud_storage'].get_object(cloud_params, backup_file_name)
        backup_file = tempfile.NamedTemporaryFile()
        backup_file.write(backup_object['Body'].read())
        if backup_file_name.split('|')[0][-4:] == '.enc':
            passphrase = config.get('odoo_backup_encryption_password')
            if not passphrase:
                raise UserError(_(
                    'The backup are encrypted. But encryption password is not found. Please check your module settings.'
                ))
            # GnuPG ignores the --output parameter with an existing file object as value
            decrypted_backup_file = tempfile.NamedTemporaryFile()
            decrypted_backup_file_name = decrypted_backup_file.name
            os.unlink(decrypted_backup_file_name)
            gnupg.GPG().decrypt_file(backup_file, passphrase=passphrase, output=decrypted_backup_file_name)
            backup_file = open(decrypted_backup_file_name, 'rb')
        try:
            db.restore_db(name, backup_file.name, str2bool(copy))
            # Make all auto backup cron records inactive
            with closing(db_connect(name).cursor()) as cr:
                cr.autocommit(True)
                cr.execute("""
                    UPDATE ir_cron SET active=false
                    WHERE active=true AND id IN (SELECT ir_cron_id FROM odoo_backup_sh_config_cron);

                    UPDATE odoo_backup_sh_config SET active=false WHERE active=true;
                """)
            return http.local_redirect('/web/database/manager')
        except Exception as e:
            error = "Database restore error: %s" % (str(e) or repr(e))
            return env.get_template("backup_list.html").render(error=error)
        finally:
            os.unlink(backup_file.name)

    @http.route('/odoo_backup_sh/fetch_dashboard_data', type="json", auth='user')
    def fetch_dashboard_data(self):
        date_month_before = datetime.now().date() - timedelta(days=29)
        date_list = [date_month_before + timedelta(days=x) for x in range(30)]
        last_month_domain = [('date', '>=', datetime.strftime(date_list[0], DEFAULT_SERVER_DATE_FORMAT))]
        usage_values = {
            datetime.strptime(r.date, DEFAULT_SERVER_DATE_FORMAT).date(): r.total_used_remote_storage for r in
            request.env['odoo_backup_sh.remote_storage'].search(last_month_domain).sorted(key='date')
        }
        for date in date_list:
            if date not in usage_values:
                if date_list.index(date) == 0:
                    usage_values[date] = 0
                else:
                    usage_values[date] = usage_values.get(date_list[date_list.index(date) - 1], 0)
        dashboard_data = {
            'remote_storage_usage_graph_values': [{
                'key': 'Remote Storage Usage',
                'values': [{
                    0: fields.Date.to_string(day),
                    1: usage_values[day]
                } for day in date_list]
            }]
        }

        last_week_dates = date_list[-7:]
        backup_configs = request.env['odoo_backup_sh.config'].with_context({'active_test': False}).search_read(
            [], ['database', 'active'])
        for b_config in backup_configs:
            graph_values = {date: 0 for date in last_week_dates}
            for backup in request.env['odoo_backup_sh.backup_info'].search([
                    ('database', '=', b_config['database']),
                    ('upload_datetime', '>=', datetime.strftime(last_week_dates[0], DEFAULT_SERVER_DATETIME_FORMAT))]):
                graph_values[datetime.strptime(backup.upload_datetime, DEFAULT_SERVER_DATETIME_FORMAT).date()] +=\
                    backup.backup_size
            b_config['graph'] = [{
                'key': 'Backups of Last 7 Days',
                'values': [{
                    'label': 'Today' if date == last_week_dates[-1] else datetime.strftime(date, '%d %b'),
                    'value': graph_values[date],
                } for date in last_week_dates]
            }]
            b_config.update({
                'backups_number': request.env['odoo_backup_sh.backup_info'].search_count([
                    ('database', '=', b_config['database'])]),
                'graph': [{
                    'key': 'Backups of Last 7 Days',
                    'values': [{
                        'label': 'Today' if date == last_week_dates[-1] else datetime.strftime(date, '%d %b'),
                        'value': graph_values[date],
                    } for date in last_week_dates]
                }]
            })
        dashboard_data['configs'] = backup_configs
        dashboard_data.update({
            'configs': backup_configs,
            'notifications': request.env['odoo_backup_sh.notification'].search_read(
                [('is_read', '=', False)], ['id', 'date_create', 'message'])
        })
        return dashboard_data
