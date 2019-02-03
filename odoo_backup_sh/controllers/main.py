# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import jinja2
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
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import str2bool
from odoo.addons import web
from odoo.addons.web.controllers.main import DBNAME_PATTERN

try:
    from pretty_bad_protocol import gnupg
except ImportError as err:
    logging.getLogger(__name__).debug(err)

path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
loader = jinja2.FileSystemLoader(path)
env = jinja2.Environment(loader=loader, autoescape=True)
BACKUP_SERVICE_ENDPOINT = 'https://odoo-backup.sh'


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
            d['list_db'] = odoo.tools.config['list_db']
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
        cloud_params = request.env['odoo_backup_sh.odoo_tools_config'].get_values('options', [
            'odoo_backup_user_key', 'amazon_bucket_name', 'amazon_access_key_id', 'amazon_secret_access_key',
            'odoo_oauth_uid'])
        if None in cloud_params.values():
            if redirect:
                cloud_params = cls.update_cloud_params(cloud_params, redirect)
            else:
                # This case occurs when we cannot pass the redirect param, ex. the request was sent by a cron
                raise UserError(_("You don't have credentials to access to cloud storage. "
                                  "Please go to the backup dashboard menu"))
        return cloud_params

    @classmethod
    def update_cloud_params(cls, cloud_params, redirect):
        user_key = cloud_params['odoo_backup_user_key']
        if not user_key:
            user_key = ''.join(random.choice(string.hexdigits) for _ in range(30))
            request.env['odoo_backup_sh.odoo_tools_config'].set_values('options', {'odoo_backup_user_key': user_key})
        cloud_params = requests.get(BACKUP_SERVICE_ENDPOINT + '/get_cloud_params', params={
            'user_key': user_key,
            'redirect': redirect,
        }).json()
        if 'insufficient_credit_error' in cloud_params:
            existing_msg = request.env['odoo_backup_sh.notification'].sudo().search(
                [('type', '=', 'insufficient_credits'), ('is_read', '=', False)])
            notification_vals = {
                'date_create': datetime.now(),
                'type': 'insufficient_credits',
                'message': cloud_params['insufficient_credit_error']
            }
            if existing_msg:
                existing_msg.write(notification_vals)
            else:
                request.env['odoo_backup_sh.notification'].sudo().create(notification_vals)
        elif 'auth_link' not in cloud_params:
            request.env['odoo_backup_sh.odoo_tools_config'].sudo().set_values('options', cloud_params)
            request.env['odoo_backup_sh.notification'].sudo().search(
                [('type', 'in', ['insufficient_credits', 'forecast_insufficient_credits']), ('is_read', '=', False)]
            ).unlink()
        return cloud_params

    @http.route('/web/database/backups', type='http', auth="none")
    def backup_list(self):
        cloud_params = self.get_cloud_params(request.httprequest.url)
        page_values = {
            'backup_list': [],
            'pattern': DBNAME_PATTERN,
            'insecure': odoo.tools.config.verify_admin_password('admin')
        }
        if 'auth_link' in cloud_params:
            return "<html><head><script>window.location.href = '%s';</script></head></html>" % cloud_params['auth_link']
        elif 'insufficient_credit_error' in cloud_params:
            page_values['error'] = cloud_params['insufficient_credit_error']
            return env.get_template("backup_list.html").render(page_values)
        backup_list = request.env['odoo_backup_sh.cloud_storage'].get_backup_list(cloud_params)
        if 'reload_page' in backup_list:
            page_values['error'] = 'Something went wrong. Please refresh the page.'
            return env.get_template("backup_list.html").render(page_values)
        page_values['backup_list'] = [name for name in backup_list['backup_list'] if name[-5:] != '.info']
        return env.get_template("backup_list.html").render(page_values)

    @http.route('/web/database/restore_via_odoo_backup_sh', type='http', auth="none", methods=['POST'], csrf=False)
    def restore_via_odoo_backup_sh(self, master_pwd, backup_file_name, name, copy=False):
        cloud_params = self.get_cloud_params(request.httprequest.url)
        backup_object = request.env['odoo_backup_sh.cloud_storage'].get_object(cloud_params, backup_file_name)
        backup_file = tempfile.NamedTemporaryFile()
        backup_file.write(backup_object['Body'].read())
        if backup_file_name.split('|')[0][-4:] == '.enc':
            passphrase = request.env['odoo_backup_sh.odoo_tools_config'].get_values(
                'options', ['odoo_backup_encryption_password'])['odoo_backup_encryption_password']
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
