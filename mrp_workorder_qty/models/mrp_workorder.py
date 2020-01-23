# Copyright 2020 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpWorkorder(models.Model):

    _inherit = 'mrp.workorder'

    def do_finish(self):
        self.ensure_one()
        produced = self.qty_produced + self.qty_producing
        if produced > self.qty_production:
            self.production_id.product_qty = produced
        res = super(MrpWorkorder, self).do_finish()
        return res

    def button_force_workorder(self):
        self.ensure_one()
        new_produced = self.qty_produced + self.qty_producing
        self.production_id.product_qty = new_produced
        if self.next_work_order_id:
            self.next_work_order_id.qty_producing = new_produced
        return self.do_finish()
