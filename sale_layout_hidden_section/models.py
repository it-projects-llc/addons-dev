# Copyright 2017 Artyom Losev
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class SaleLayoutCategory(models.Model):
    _inherit = 'sale.layout_category'

    sale_order_id = fields.Many2one('sale.order')
    is_global = fields.Boolean(default=False, string='Global')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        record = super(SaleOrderLine, self).create(vals)
        if record.layout_category_id and not record.layout_category_id.sale_order_id:
            record.layout_category_id.sale_order_id = record.order_id
        return record


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    layout_ids = fields.One2many('sale.layout_category', 'sale_order_id', string='Order Sections')

    @api.onchange('order_line')
    def on_layout_changing(self):
        self.layout_ids = False
        for line in self.order_line:
            if line.layout_category_id:
                self.layout_ids += line.layout_category_id
