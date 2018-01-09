# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError
from ..wizard.price_finder import _find_insurance_product


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def _get_fiscal_power(self):
        for record in self.filtered('fuel_type'):
            fiscal_power = self.env['insurance_pricing.fiscal_power'].search([(record.fuel_type, '=', True),
                                                                            ('{}_horsepower_from'.format(record.fuel_type), '<=', record.horsepower),
                                                                            ('{}_horsepower_to'.format(record.fuel_type), '>=', record.horsepower)])
            if fiscal_power:
                record.product_attribute_value_id = fiscal_power[0].product_attribute_value_id.id

    category_id = fields.Many2one('product.category', 'Category', required=True)
    product_attribute_value_id = fields.Many2one('product.attribute.value', 'Fiscal Power',
                                                 domain=lambda self: [('attribute_id', '=', self.env.ref('insurance_pricing.product_attribute_fiscal_power').id)],
                                                 compute='_get_fiscal_power', readonly=True)
    product_id = fields.Many2one('product.product', 'Vehicle Insurance', compute=_find_insurance_product, readonly=True)
    base_price = fields.Float('Price', related='product_id.lst_price', digits=dp.get_precision('Product Price'), readonly=True)
    fuel_type = fields.Selection(required=True)
    seats = fields.Integer(required=True)
    horsepower = fields.Integer(required=True)

    @api.constrains('horsepower')
    def _check_horsepower(self):
        if any(vehicle.horsepower < 2 for vehicle in self):
            raise ValidationError(_('Error ! Horsepower value should not be less than two.'))
        return True
