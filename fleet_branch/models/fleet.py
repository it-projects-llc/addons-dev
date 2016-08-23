# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models


class Vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    branch_id = fields.Many2one('fleet_branch.branch', string='Current branch')
