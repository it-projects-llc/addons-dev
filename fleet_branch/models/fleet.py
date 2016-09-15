# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models
from openerp import api


class Vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    branch_id = fields.Many2one('fleet_branch.branch', string='Current branch')
    color_id = fields.Many2one(track_visibility='onchange')
    state_id = fields.Many2one(track_visibility='onchange')


    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state_id' in init_values:
            return 'fleet_branch.mt_vehicle_fleet'
        return super(Vehicle, self)._track_subtype(init_values)
