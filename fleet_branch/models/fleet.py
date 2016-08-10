# -*- coding: utf-8 -*-
from openerp import api, fields, models


class Vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    branch_id = fields.Many2one('fleet_branch.branch', string='Current branch')
