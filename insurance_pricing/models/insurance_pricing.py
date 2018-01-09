# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class FiscalPower(models.Model):
    _name = 'insurance_broker.fiscal_power'
    _description = "Fiscal Power"
    _rec_name = 'product_attribute_value_id'
    _order = "product_attribute_value_id"

    active = fields.Boolean("Active", default=True)
    diesel = fields.Boolean("Diesel", default=True)
    diesel_horsepower_from = fields.Integer("HP Diesel from", default=True)
    diesel_horsepower_to = fields.Integer("HP Diesel to")
    gasoline = fields.Boolean("Gasoline", default=True)
    gasoline_horsepower_from = fields.Integer("HP Gasoline from", default=True)
    gasoline_horsepower_to = fields.Integer("HP Gasoline to")
    electric = fields.Boolean("Electric")
    electric_horsepower_from = fields.Integer("HP Electric from")
    electric_horsepower_to = fields.Integer("HP Electric to")
    hybrid = fields.Boolean("Hybrid")
    hybrid_horsepower_from = fields.Integer("HP Hybrid from")
    hybrid_horsepower_to = fields.Integer("HP Hybrid to")
    product_attribute_value_id = fields.Many2one('product.attribute.value', 'Fiscal Power',
                                                 domain=lambda self: [('attribute_id', '=', self.env.ref('insurance_broker_car_pricing.product_attribute_fiscal_power').id)],
                                                 required=True)

    # This constraint is not tested yet, but it must work , at the end of the day
    # _sql_constraints = [('key_unique', 'UNIQUE(\
    #                      product_attribute_value_id, active, \
    #                      diesel, diesel_horsepower_from, diesel_horsepower_to, \
    #                      gasoline, gasoline_horsepower_from, gasoline_horsepower_to, \
    #                      electric, electric_horsepower_from, electric_horsepower_to, \
    #                      hybrid, hybrid_horsepower_from, hybrid_horsepower_to)',\
    #                      'This fiscal power pricing condition already exists in the system.')]
