# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    color_id = fields.Many2one('fleet.vehicle_color', string='Color', help='Color of the vehicle')
