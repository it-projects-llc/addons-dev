# -*- coding: utf-8 -*-
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    orders_history = fields.Boolean("Orders History", help="Show all orders list in POS", default=False)
