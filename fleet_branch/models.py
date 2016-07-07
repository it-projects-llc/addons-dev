# -*- coding: utf-8 -*-

from openerp import api, fields, models


# INHERITED MODELS

class Branch(models.Model):

    _name = "fleet_branch.branch"
    _inherit = 'hr.department'

    city = fields.Char(string='City')
    phone = fields.Char(string='Phone')
    branch_target = fields.Char(string='Branch Target')
    users_ids = fields.One2many('res.users', 'branch_id')
    state = fields.Selection([('new', 'New'),
                              ('active', 'Active')],
                             string='State', default='new')


class User(models.Model):
    _inherit = 'res.users'

    branch_id = fields.Many2one('fleet_branch.branch')


class Vehicle(models.Model):

    _inherit = 'fleet.vehicle'

    branch_id = fields.Many2one('fleet_branch.branch', string='Current branch')
