# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from ..controllers.main import BackupController


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    encrypt_backups = fields.Boolean(string="Encrypt Backups")
    encryption_password = fields.Char(string='Encryption Password')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icp_get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update({
            'encrypt_backups': icp_get_param('odoo_backup_sh.encrypt_backups', 'False').lower() == 'true',
            'encryption_password': icp_get_param('odoo_backup_sh.encryption_password'),
        })
        return res

    @api.multi
    def set_values(self):
        icp_set_param = self.env['ir.config_parameter'].sudo().set_param
        # we store the repr of the value, since the value of the parameter is a required string
        icp_set_param('odoo_backup_sh.encrypt_backups', repr(self.encrypt_backups))
        icp_set_param('odoo_backup_sh.encryption_password', self.encryption_password)
        super(ResConfigSettings, self).set_values()
