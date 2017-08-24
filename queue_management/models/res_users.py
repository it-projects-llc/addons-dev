# -*- encoding: utf-8 -*-
from openerp import fields
from openerp import models


class ResUsers(models.Model):
    _inherit = 'res.users'
    service_ids = fields.Many2many('queue.management.service', string="Services", required=True)
