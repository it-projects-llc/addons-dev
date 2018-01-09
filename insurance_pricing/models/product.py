# -*- coding: utf-8 -*-
# © 2017 Ergobit Consulting (https://www.ergobit.org)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.addons import decimal_precision as dp


class ProductCategory(models.Model):
    _inherit = "product.category"

    @api.multi
    def name_get(self):
        fleet_categ_ids =[self.env.ref('insurance_pricing.product_category_pool').id, self.env.ref('insurance_pricing.product_category_non_pool').id]
        fleet_categs = self.filtered(lambda r: r.id in fleet_categ_ids)
        other_categs = self - fleet_categs

        other_list = super(ProductCategory, other_categs).name_get()
        fleet_list = [(cat.id, cat.name) for cat in fleet_categs]

        return other_list + fleet_list


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
