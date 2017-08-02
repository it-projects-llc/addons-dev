# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    flip_image = fields.Binary(string='Flip image', attachment=True,
                               help="Flip image will be shown on mouse hover in website on specific product.")

class KingProductImages(models.Model):
    _inherit = 'biztech.product.images'

    image = fields.Binary(string='Image', attachment=True)
