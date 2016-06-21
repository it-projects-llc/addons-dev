# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class FleetVehicleRental(models.Model):
    _inherit = 'fleet.vehicle'

    allowed_kilometer_per_day = fields.Integer(string='Allowed kilometer per day')

    rate_per_extra_km = fields.Float(string='Rate per extra km', digits_compute=dp.get_precision('Product Price'))

    daily_rental_price = fields.Float(string='Daily Rental Price', digits_compute=dp.get_precision('Product Price'))
