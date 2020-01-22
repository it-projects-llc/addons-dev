# Copyright 2020 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpWorkorder(models.Model):

    _inherit = 'mrp.workorder'

    def button_force_workorder(self):
        self.ensure_one()
        self.production_id.product_qty = self.qty_produced + self.qty_producing
        return self.do_finish()
