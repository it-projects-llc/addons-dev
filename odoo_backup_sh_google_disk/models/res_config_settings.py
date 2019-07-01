# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    google_service_account_file = fields.Char(string="Service Account File path",
                                              help="Specify path to service account file")
    google_disk_folder_id = fields.Char(string="Google Drive Folder ID")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("odoo_backup_sh_google_disk.service_account_file", self.google_service_account_file or '')
        ICPSudo.set_param("odoo_backup_sh_google_disk.google_disk_folder_id", self.google_disk_folder_id or '')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        google_service_account_file = ICPSudo.get_param("odoo_backup_sh_google_disk.service_account_file")
        google_disk_folder_id = ICPSudo.get_param("odoo_backup_sh_google_disk.google_disk_folder_id")
        res.update(
            google_service_account_file=google_service_account_file or False,
            google_disk_folder_id=google_disk_folder_id or False,
        )
        return res
