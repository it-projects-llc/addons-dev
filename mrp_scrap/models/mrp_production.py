# Copyright 2020 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import math

from odoo import api, fields, models


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    scrap_percent = fields.Float(related='product_id.product_tmpl_id.scrap_percent')

    def change_prod_qty(self, qty):
        self.ensure_one()
        update_qty = self.env['change.production.qty'].create({
            'mo_id': self.id,
            'product_qty': qty
        })
        update_qty.change_prod_qty()

    def button_apply_scrap(self):
        self.ensure_one()
        qty = math.ceil(self.product_qty * self.scrap_percent / 100 + self.product_qty)
        self.change_prod_qty(qty)
