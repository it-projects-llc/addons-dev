# -*- coding: utf-8 -*-
# Copyright 2017 IT-Projects LLC (<https://it-projects.info>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openerp import models, fields, api

from ..xmlrpc import rpc_execute_kw, rpc_auth


class UpdateData(models.TransientModel):
    _name = 'apps_odoo_com.update_data'

    @api.model
    def _get_repos(self):
        auth = rpc_auth(self.env)
        if not auth:
            return []
        search_read = rpc_execute_kw(
            self.env,
            'loempia.repo',
            'search_read',
            rpc_kwargs={
                'fields': ['url'],
            })
        res = [(r.get('id'), r.get('url'))
               for r in sorted(search_read,
                               key=lambda r: r.get('url')
                               )]
        return res

    @api.multi
    def get_new_data(self):
        self.ensure_one()

    @api.multi
    def get_all_data(self):
        self.ensure_one()
