# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_odoo_backup_sh_google_disk = fields.Boolean(string="Google Drive", help="Use Google Drive to store Database")
    module_odoo_backup_sh_dropbox = fields.Boolean(string="Dropbox", help="Use Dropbox to store Database")
    available_module_odoo_backup_sh_dropbox = fields.Boolean()
    available_module_odoo_backup_sh_google_disk = fields.Boolean()
    odoo_backup_sh_amazon_bucket_name = fields.Char("S3 Bucket", config_parameter='amazon_bucket_name', default='')
    odoo_backup_sh_amazon_access_key_id = fields.Char("Access Key ID", config_parameter='amazon_access_key_id', default='')
    odoo_backup_sh_amazon_secret_access_key = fields.Char("Secret Access Key", config_parameter='amazon_secret_access_key', default='')

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrModule = self.env['ir.module.module']
        for m in ['odoo_backup_sh_google_disk', 'odoo_backup_sh_dropbox']:
            res['available_module_' + m] = bool(IrModule.sudo().search([('name', '=', m)], limit=1))
        print ('get_values', res)
        return res
