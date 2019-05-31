# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_odoo_backup_sh_google_disk = fields.Boolean(string="Google Drive", help="Use Google Drive to store Database")
    module_odoo_backup_sh_dropbox = fields.Boolean(string="Dropbox", help="Use Dropbox to store Database")
