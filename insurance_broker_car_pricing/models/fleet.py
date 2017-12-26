# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def _get_fiscal_power(self):
        for record in self:
            record.product_attribute_value_id = self.env.ref('insurance_broker_car_pricing.product_attribute_fp_value_fp1').id

    def _find_insurance_product(self):
        for record in self:
            record.product_id = self.env.ref('insurance_broker_car_pricing.product_product_cat1_fp2').id

    category_id = fields.Many2one('product.category', 'Category', required=True)
    product_attribute_value_id = fields.Many2one('product.attribute.value', 'Fiscal Power',
                                                 domain=lambda self: [('attribute_id', '=', self.env.ref('insurance_broker_car_pricing.product_attribute_fiscal_power').id)],
                                                 compute='_get_fiscal_power', readonly=True)
    product_id = fields.Many2one('product.product', 'Vehicle Insurance', compute='_find_insurance_product', readonly=True)
    base_price = fields.Float('Price', related='product_id.lst_price', digits=dp.get_precision('Product Price'), readonly=True)
    fuel_type = fields.Selection(required=True)
    seats = fields.Integer(required=True)
    horsepower = fields.Integer(required=True)
