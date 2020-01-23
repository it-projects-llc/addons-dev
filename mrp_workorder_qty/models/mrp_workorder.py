# Copyright 2020 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpWorkorder(models.Model):

    _inherit = 'mrp.workorder'

    def button_force_workorder(self):
        self.ensure_one()
        new_produced = self.qty_produced + self.qty_producing
        self.production_id.product_qty = new_produced
        work_order_ids = self.env['mrp.workorder'].search([('production_id', '=', self.production_id.id)])
        work_order_ids.write({
            'qty_producing': new_produced
        })

        return self.do_finish()
