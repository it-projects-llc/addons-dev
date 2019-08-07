# Copyright 2017 IT-Projects LLC (<https://it-projects.info>)
# Copyright 2019 Anvar Kildebekov (<https://it-projects.info/team/fedoranvar>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Apps Store Credentials'

    apps_login = fields.Char("Email", help="login of your account at apps.odoo.com")
    apps_password = fields.Char("Password", help="Password for apps.odoo.com. Note, that it's not the same as password for odoo.com, check README for more information")

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        for record in self:
            config_parameters.set_param("apps_odoo_com.login", record.apps_login)
            config_parameters.set_param("apps_odoo_com.password", record.apps_password)

    @api.multi
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        apps_login = config_parameters.get_param("apps_odoo_com.login", default='')
        apps_password = config_parameters.get_param("apps_odoo_com.password", default='')
        res.update(
            apps_login=str(apps_login),
            apps_password=str(apps_password),
        )
        return res
