# -*- coding: utf-8 -*-
# Copyright 2017 IT-Projects LLC (<https://it-projects.info>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openerp import models, fields, api

PARAMS = [
    ("apps_login", "apps_odoo_com.login"),
    ("apps_password", "apps_odoo_com.password"),
]


class Settings(models.TransientModel):

    _name = 'apps_odoo_com.settings'
    _inherit = 'res.config.settings'

    apps_login = fields.Char("Email", help="login of your account at apps.odoo.com")
    apps_password = fields.Char("Password", help="Password for apps.odoo.com. Note, that it's not the same as password for odoo.com, chect README for more information")

    @api.multi
    def set_params(self):
        self.ensure_one()

        for field_name, key_name in PARAMS:
            value = getattr(self, field_name, '').strip()
            self.env['ir.config_parameter'].set_param(key_name, value)

    @api.multi
    def get_default_params(self):
        res = {}
        for field_name, key_name in PARAMS:
            res[field_name] = self.env['ir.config_parameter'].get_param(key_name, '').strip()
        return res
