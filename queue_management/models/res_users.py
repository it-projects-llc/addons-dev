# -*- encoding: utf-8 -*-
from odoo import fields
from odoo import models


class ResUsers(models.Model):
    _inherit = 'res.users'
    service_ids = fields.Many2many('queue.management.service', string="Services")
