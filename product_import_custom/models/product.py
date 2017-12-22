# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):

    _inherit = 'product.template'
    x_template_code = fields.Char('Importing code', index=True)
