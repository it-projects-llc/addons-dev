# -*- coding: utf-8 -*-
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

import odoo
from odoo import http, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools import config
from odoo.tools.misc import str2bool
from odoo.addons import web
from odoo.addons.web.controllers.main import DBNAME_PATTERN
from odoo.addons.iap import jsonrpc, InsufficientCreditError
from odoo.service import db

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

    def get_cloud_params(self):
        cloud_params = {}
        p = ConfigParser.RawConfigParser()
        p.read([config.rcfile])
        for (name, value) in p.items('options'):
            if name in ['amazon_bucket_name', 'amazon_access_key', 'amazon_secret_access_key', 'oauth_uid',
                        'odoo_backup_user_key'] and value:
                cloud_params[name] = value
        if not cloud_params.get('odoo_backup_user_key'):
            user_key = ''.join(random.choice(string.hexdigits) for _ in range(30))
            config.__setitem__('odoo_backup_user_key', user_key)
            config.save()
            cloud_params['odoo_backup_user_key'] = user_key
        return cloud_params

    def load_backup_list(self, credentials):
        s3_client = boto3.client('s3', aws_access_key_id=credentials['amazon_access_key'],
                                 aws_secret_access_key=credentials['amazon_secret_access_key'])
        user_dir_name = '%s/' % credentials['oauth_uid']
        s3_user_dir_info = s3_client.list_objects_v2(
            Bucket=credentials['amazon_bucket_name'], Prefix=user_dir_name, Delimiter='/')
        backup_list = []
        for obj in s3_user_dir_info.get('Contents', {}):
            if obj.get('Size'):
                backup_list.append(obj['Key'][len(user_dir_name):])
        return backup_list

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

    def update_info(self, redirect):
        cloud_params = self.get_cloud_params()
        if all(cloud_params.get(i) for i in
               ['amazon_bucket_name', 'amazon_access_key', 'amazon_secret_access_key', 'oauth_uid']):
            try:
                res = {'backup_list': self.load_backup_list(cloud_params)}
                credit_url = self.check_insufficient_credit(credit=10)
                if credit_url:
                    res['credit_url'] = credit_url
                return res
            except botocore.exceptions.ClientError as e:
                if isinstance(e, dict):
                    status_code = e['ResponseMetadata']['HTTPStatusCode']
                else:
                    status_code = e.response['ResponseMetadata']['HTTPStatusCode']
                if status_code == 403:
                    # Delete local cloud parameters and receive it again to make sure they are up-to-date.
                    for key in ['amazon_bucket_name', 'amazon_access_key', 'amazon_secret_access_key', 'oauth_uid']:
                        config.__setitem__(key, '')
                    config.save()
                    return {'reload_page': True}
                else:
                    # Show message of another errors
                    error = "Amazon Web Services error: %s" % e.response['Error']['Message']
                    return {'error': error}
        else:
            response = requests.get(
                BACKUP_SERVICE_ENDPOINT + '/get_cloud_params',
                params={'user_key': cloud_params['odoo_backup_user_key'], 'redirect': redirect}
            ).json()
            if 'auth_link' not in response:
                for credential_key, credential_value in response.items():
                    config.__setitem__(credential_key, credential_value)
                config.save()
                try:
                    res = {'backup_list': self.load_backup_list(response)}
                    credit_url = self.check_insufficient_credit(credit=10)
                    if credit_url:
                        res['credit_url'] = credit_url
                    return res
                except botocore.exceptions.ClientError as e:
                    error = "Amazon S3 error: %s" % e.response['Error']['Message']
                    return {'error': error}
            else:
                return response

    @http.route('/web/database/backups', type='http', auth="none")
    def backup_list(self):
        redirect = request.httprequest.url
        res = self.update_info(redirect)
        if 'auth_link' in res:
            return "<html><head><script>window.location.href = '%s';</script></head></html>" % res['auth_link']
        elif 'reload_page' in res:
            return "<html><head><script>window.location.href = '%s';</script></head></html>" % request.httprequest.url
        else:
            d = {
                'backup_list': res.get('backup_list'),
                'error': res.get('error'),
                'pattern': DBNAME_PATTERN,
                'insecure': odoo.tools.config.verify_admin_password('admin')
            }
            return env.get_template("backup_list.html").render(d)

    @http.route('/web/database/restore_via_odoo_backup_sh', type='http', auth="none", methods=['POST'], csrf=False)
    def restore_via_odoo_backup_sh(self, master_pwd, backup_file_name, name, copy=False):
        cloud_params = self.get_cloud_params()
        s3_client = boto3.client('s3', aws_access_key_id=cloud_params['amazon_access_key'],
                                 aws_secret_access_key=cloud_params['amazon_secret_access_key'])
        backup_file_path = '%s/%s' % (cloud_params['oauth_uid'], backup_file_name)
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
            return http.local_redirect('/web/database/manager')
        except Exception as e:
            error = "Database restore error: %s" % (str(e) or repr(e))
            return env.get_template("backup_list.html").render(error=error)
        finally:
            os.unlink(backup_file.name)
