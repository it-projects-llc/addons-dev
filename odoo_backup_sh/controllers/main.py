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

import odoo
from odoo import http, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.service import db
from odoo.sql_db import db_connect
from odoo.tools import config
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

    def get_cloud_params(self, redirect=None):
        config_parser.read(config.rcfile)
        cloud_params = {}
        for name in ['odoo_backup_user_key', 'amazon_bucket_name', 'amazon_access_key', 'amazon_secret_access_key',
                     'odoo_oauth_uid']:
            cloud_params[name] = config_parser.get('options', name, fallback=None)
        if None in cloud_params.values() and redirect:
            cloud_params = self.update_cloud_params(cloud_params, redirect)
        return cloud_params

    def update_cloud_params(self, cloud_params, redirect):
        user_key = cloud_params['odoo_backup_user_key']
        if not user_key:
            user_key = ''.join(random.choice(string.hexdigits) for _ in range(30))
            config_parser.set('options', 'odoo_backup_user_key', user_key)
            with open(config.rcfile, 'w') as configfile:
                config_parser.write(configfile)
        cloud_params = requests.get(
            BACKUP_SERVICE_ENDPOINT + '/get_cloud_params',
            params={'user_key': user_key, 'redirect': redirect}
        ).json()
        if 'auth_link' not in cloud_params:
            for param_key, param_value in cloud_params.items():
                config_parser.set('options', param_key, param_value)
            with open(config.rcfile, 'w') as configfile:
                config_parser.write(configfile)
            cloud_params['updated'] = True  # The mark that all params are updated
        return cloud_params

    def load_backup_list(self, cloud_params):
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
                with open(config.rcfile, 'w') as configfile:
                    config_parser.write(configfile)
                return {'reload_page': True}
            else:
                return {'error': "Amazon Web Services error: %s" % e.response['Error']['Message']}
        backup_list = [
            obj['Key'][len(user_dir_name):] for obj in s3_user_dir_info.get('Contents', {}) if obj.get('Size')]
        return {'backup_list': backup_list}

    def check_insufficient_credit(self, credit):
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
        s3_client = boto3.client('s3', aws_access_key_id=cloud_params['amazon_access_key'],
                                 aws_secret_access_key=cloud_params['amazon_secret_access_key'])
        backup_file_path = '%s/%s' % (cloud_params['odoo_oauth_uid'], backup_file_name)
        backup_object = s3_client.get_object(Bucket=cloud_params['amazon_bucket_name'], Key=backup_file_path)
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
            # Make all auto backup cron recors inactive
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
