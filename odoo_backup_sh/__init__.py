# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from . import controllers
from . import models
from odoo import api, SUPERUSER_ID


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    backup_crons = env['odoo_backup_sh.config.cron'].search([('model_name', '=', 'odoo_backup_sh.config')])
    if backup_crons:
        backup_crons.unlink()
