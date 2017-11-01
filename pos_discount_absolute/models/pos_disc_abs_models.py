# -*- coding: utf-8 -*-

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    discount_abs_value = fields.Float(string='Absolute Discount value', default=0, help='The default discount value')
    discount_abs_enabled = fields.Boolean(string='Use absolute discount type', default=False, help='Discount type')
    discount_abs_product_id = fields.Many2one('product.product', string='Absolute Discount Product', domain="[('available_in_pos', '=', True)]", help='The product used to model an absolute discount')
    discount_product_id = fields.Many2one(string='Relative Discount Product', help='The product used to model a relative discount')
