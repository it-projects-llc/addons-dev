# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hot_product = fields.Boolean(string='Hot Product', help='Check if you this product is hot product (promotion)',
                                 default=False)
    hot_product_image_ids = fields.One2many('product.hot.image', 'product_tmpl_id', string='Images',
                                            help='Hot Product images (shows like slide show on mini program)')


class ProductHotImage(models.Model):
    _name = 'product.hot.image'

    name = fields.Char('Name')
    image = fields.Binary('Image', attachment=True)
    product_tmpl_id = fields.Many2one('product.template', 'Related Product', copy=True)
