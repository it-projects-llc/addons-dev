# -*- coding: utf-8 -*-
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


def _find_insurance_product(self):
    for record in self:
        AttrVal = self.env['product.attribute.value']
        fiscal_power_products = record.product_attribute_value_id.product_ids
        if record.seats:
            seats_products = AttrVal.search([('attribute_id', '=', self.env.ref('insurance_broker_car_pricing.product_attribute_seats').id),
                                             ('name', '=', str(record.seats))]).product_ids
            products = seats_products & fiscal_power_products
        else:
            products = fiscal_power_products
        products = products.filtered(lambda r: r.categ_id == record.category_id)
        if products:
            record.product_id = products[0].id


class InsuranceBrokerPriceFinder(models.TransientModel):
    _name = "insurance_broker.price.finder"
    _description = "Price Finder"


    category_id = fields.Many2one('product.category', 'Category', required=True)
    product_attribute_value_id = fields.Many2one('product.attribute.value', 'Fiscal Power',
                                                 domain=lambda self: [('attribute_id', '=', self.env.ref('insurance_broker_car_pricing.product_attribute_fiscal_power').id)])
    seats = fields.Integer()
    product_id = fields.Many2one('product.product', 'Vehicle Insurance', compute=_find_insurance_product, readonly=True)
    base_price = fields.Float('Price', related='product_id.lst_price', digits=dp.get_precision('Product Price'), readonly=True)
