# -*- coding: utf-8 -*-
from openerp import models, fields, api


class FleetRentalAdditionalDriver(models.Model):
    _inherit = 'personal.drive_license'
    _name = 'fleet_rental.additional_driver'

    name = fields.Char(string='Driver Name')
