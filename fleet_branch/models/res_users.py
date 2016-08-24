# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models


class User(models.Model):
    _inherit = 'res.users'

    branch_id = fields.Many2one('fleet_branch.branch')
