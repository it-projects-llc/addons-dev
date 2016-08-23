# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models


class FleetVehicleColor(models.Model):
    _name = 'fleet.vehicle_color'

    name = fields.Char(string='Vehicle Color', required=True)

    color = fields.Char(
        string="Color",
        help="Choose your color"
    )
