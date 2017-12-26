# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class FiscalPower(models.Model):
    _name = 'insurance_broker.fiscal_power'
    _description = "Fiscal Power"
    _rec_name = 'product_attribute_value_id'

    @api.model
    def _get_fuel_types(self):
        FleetVehicle = self.env['fleet.vehicle']
        fuel_types = FleetVehicle._fields['fuel_type'].selection
        return fuel_types

    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide the product without removing it.")
    fuel_type = fields.Selection('_get_fuel_types', required=True)
    horsepower_from = fields.Integer(required=True)
    horsepower_to = fields.Integer(required=True)
    product_attribute_value_id = fields.Many2one('product.attribute.value', 'Fiscal Power',
                                                 domain=lambda self: [('attribute_id', '=', self.env.ref('insurance_broker_car_pricing.product_attribute_fiscal_power').id)],
                                                 required=True)
