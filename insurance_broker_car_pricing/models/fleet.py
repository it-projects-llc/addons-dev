# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def _get_fiscal_power(self):
        for record in self:
            fiscal_power = self.env['insurance_broker.fiscal_power'].search([('fuel_type', '=', record.fuel_type),
                                                                            ('horsepower_from', '<=', record.horsepower),
                                                                            ('horsepower_to', '>=', record.horsepower)])
            if fiscal_power:
                record.product_attribute_value_id = fiscal_power[0].product_attribute_value_id.id

    def _find_insurance_product(self):
        for record in self:
            AttrVal = self.env['product.attribute.value']
            seats_products = AttrVal.search([('attribute_id', '=', self.env.ref('insurance_broker_car_pricing.product_attribute_seats').id),
                                             ('name', '=', str(record.seats))]).product_ids
            fiscal_power_products = record.product_attribute_value_id.product_ids
            products = seats_products & fiscal_power_products
            products.filtered(lambda r: r.categ_id == record.category_id.id)
            if products:
                record.product_id = products[0].id

    category_id = fields.Many2one('product.category', 'Category', required=True)
    product_attribute_value_id = fields.Many2one('product.attribute.value', 'Fiscal Power',
                                                 domain=lambda self: [('attribute_id', '=', self.env.ref('insurance_broker_car_pricing.product_attribute_fiscal_power').id)],
                                                 compute='_get_fiscal_power', readonly=True)
    product_id = fields.Many2one('product.product', 'Vehicle Insurance', compute='_find_insurance_product', readonly=True)
    base_price = fields.Float('Price', related='product_id.lst_price', digits=dp.get_precision('Product Price'), readonly=True)
    fuel_type = fields.Selection(required=True)
    seats = fields.Integer(required=True)
    horsepower = fields.Integer(required=True)

    @api.constrains('horsepower')
    def _check_horsepower(self):
        if any(vehicle.horsepower < 2 for vehicle in self):
            raise ValidationError(_('Error ! Horsepower value should not be less than two.'))
        return True
