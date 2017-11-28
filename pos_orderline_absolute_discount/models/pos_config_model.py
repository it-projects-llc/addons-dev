# -*- coding: utf-8 -*-
from odoo import fields
from odoo import models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    display_price_without_discount = fields.Boolean(string="Display Price Without Discount", default=True)
