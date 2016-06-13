# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api


class FleetVehicleColor(models.Model):
    _name = 'fleet.vehicle_color'

    name = fields.Char(string='Vehicle Color', required=True)

    color = fields.Char(
        string="Color",
        help="Choose your color"
    )
