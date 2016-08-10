# -*- coding: utf-8 -*-
from openerp import api, fields, models


class User(models.Model):
    _inherit = 'res.users'

    branch_id = fields.Many2one('fleet_branch.branch')
