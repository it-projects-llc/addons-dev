# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    pos_notes = fields.Text('Notes for POS', translate=True)
