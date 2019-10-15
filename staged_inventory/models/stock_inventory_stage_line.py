# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class StockInventoryStageLine(models.Model):
    _name = "stock.inventory.stage.line"
    _rec_name = 'product_id'
    _description = 'Inventory Stage Line'

    stage_id = fields.Many2one(
        comodel_name='stock.inventory.stage',
        string='Stage',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
    )
    qty = fields.Float('Qty')
    barcode = fields.Char(
        related='product_id.barcode',
        readonly=True,
    )

    _sql_constraints = [('stock_inventory_stage_line_product_uniq',
                         'UNIQUE (stage_id, product_id)',
                         'Product must be unique for the stage!')]
