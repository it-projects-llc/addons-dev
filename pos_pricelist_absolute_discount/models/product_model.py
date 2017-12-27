# -*- coding: utf-8 -*-
import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    pos_discount_policy = fields.Selection([
        ('with_discount', 'Discount included in the price in POS'),
        ('without_discount', 'Show public price & discount to the customer in POS')],
        default='with_discount', string="POS Discount")
