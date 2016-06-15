# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    color_id = fields.Many2one('fleet.vehicle_color', string='Color', help='Color of the vehicle')
