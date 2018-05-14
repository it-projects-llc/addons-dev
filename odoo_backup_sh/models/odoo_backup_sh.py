# -*- coding: utf-8 -*-
# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import json

from odoo import api, fields, models
from ..controllers.main import BackupController, BACKUP_SERVICE_ENDPOINT
from odoo.addons.iap import jsonrpc, InsufficientCreditError


class Dashboard(models.AbstractModel):
    _name = 'odoo_backup_sh.dashboard'
    _description = 'Backup Dashboard'

    @api.model
    def action_dashboard_redirect(self):
        return self.env.ref('odoo_backup_sh.backup_dashboard').read()[0]


class Backup(models.Model):
    _name = 'odoo_backup_sh.backup'
    _description = 'Information about backups'

    backup_name = fields.Char(string='Backup Name')
    date_upload = fields.Datetime(string='Upload Date')

    @api.model
    def update_info(self, redirect):
        response = BackupController().load_backup_list_from_service(redirect=redirect)
        # TODO: save new backups list
        if 'auth_link' not in response:
            credit_url = self.check_insufficient_credit(credit=10)
            if credit_url:
                response['credit_url'] = credit_url
        return response

    @api.model
    def make_backup(self, name=None, backup_format='zip'):
        if name is None:
            name = self.env.cr.dbname
        # TODO: make dump
        # TODO: get url to upload
        # TODO: upload
        # ts = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        # filename = "%s_%s.%s" % (name, ts, backup_format)
        # dump_stream = odoo.service.db.dump_db(name, None, backup_format)
        # return dump_stream

    @api.model
    def check_insufficient_credit(self, credit):
        user_token = self.env['iap.account'].get('odoo_backup_sh')
        params = {
            'account_token': user_token.account_token,
            'cost': credit,
        }
        endpoint = BACKUP_SERVICE_ENDPOINT
        try:
            jsonrpc(endpoint + '/make_backup', params=params)
        except InsufficientCreditError as e:
            error_data = json.loads(e.data['message'])
            credit_url = self.env['iap.account'].get_credits_url(
                error_data['base_url'], error_data['service_name'], error_data['credit'])
            return credit_url
        return None
