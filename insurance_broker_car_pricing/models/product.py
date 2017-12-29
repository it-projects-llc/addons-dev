# -*- coding: utf-8 -*-
# © 2017 Ergobit Consulting (https://www.ergobit.org)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.addons import decimal_precision as dp

class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_price_extra = fields.Float(
        'Add. price /tariff', digits=dp.get_precision('Product Price'),
        help="This is the extra price on top of each variant")

    @api.depends('attribute_value_ids.price_ids.price_extra', 'attribute_value_ids.price_ids.product_tmpl_id', 'variant_price_extra')
    def _compute_product_price_extra(self):
        super(ProductProduct, self)._compute_product_price_extra()
        for product in self:
            product.price_extra += product.variant_price_extra
