# -*- coding: utf-8 -*-

from odoo import models, fields, api


class queue_management_user(models.Model):
    _name = 'queue.management.user'
    _inherit = 'res.users'
    position_id = fields.Many2one('res.groups', 'Position')
    desk = fields.Selection([('1', '1'),
                             ('2', '2')], 'Desk Number', required=True, copy=False, default='1')
    primary_service_id = fields.Many2one('queue.management.service')
    branch_id = fields.Many2one('queue.management.branch', 'Branch')

