# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models


class FleetRentalAdditionalDriver(models.Model):
    _inherit = 'personal.drive_license'
    _name = 'fleet_rental.additional_driver'

    name = fields.Char(string='Driver Name')
