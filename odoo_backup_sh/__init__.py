# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from . import controllers
from . import models
from odoo import api, SUPERUSER_ID


def uninstall_hook(cr, registry):
    # During the unistall of the module, we have the error:
    # 'update or delete on table "ir_act_server" violates foreign key constraint
    # "ir_cron_ir_actions_server_id_fkey" on table "ir_cron"'. Due to this error the "odoo_backup_sh.config" table
    # will not be deleted. Below the code allows you to delete all entries related to "ir_cron".
    env = api.Environment(cr, SUPERUSER_ID, {})
    backup_crons = env['odoo_backup_sh.config.cron'].search([('model_name', '=', 'odoo_backup_sh.config')])
    if backup_crons:
        backup_crons.unlink()
