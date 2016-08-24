# -*- coding: utf-8 -*-
from openerp import fields, models


class Asset(models.Model):
    _inherit = 'account.asset.asset'

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
