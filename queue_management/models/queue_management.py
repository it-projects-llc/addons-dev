# -*- coding: utf-8 -*-
from odoo import models, fields, api

number_of_desks = {'1': '1',
                   '2': '2',
                   '3': '3',
                   '4': '4',
                   '5': '5'}


class QueueManagementBranch(models.Model):
    _name = 'queue.management.branch'
    _inherits = {'res.company': 'company_id'}
    company_id = fields.Many2one('res.company')
    service_ids = fields.One2many('queue.management.service', 'branch_id', required=True, string="Services")


class QueueManagementLog(models.Model):
    _name = 'queue.management.log'
    ticket_id = fields.Many2one('queue.management.ticket', 'Ticket number')
    desk_id = fields.Many2one('queue.magment.user', 'Desk')
    service_id = fields.Many2one('queue.management.service', 'Service')
    ticket_state = fields.Char(string='Ticket State', related='ticket_id.name', readonly=True)


class QueueManagementTicket(models.Model):
    _name = 'queue.management.ticket'
    name = fields.Char(string='Ticket Name', readonly=True)
    service_id = fields.Many2one('queue.management.service', 'Service', required='True')
    ticket_state = fields.Selection([
        ('previous', 'Previous'),
        ('current', 'Current'),
        ('next', 'Next'),
        ('done', 'Done'),
        ('no-show', 'No-show')], 'Ticket State', required=True, copy=False, default='next')

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            service = self.env['queue.management.service'].browse(vals.get('service_id'))
            vals['name'] = service.sequence_id.next_by_id()
        return super(QueueManagementTicket, self).create(vals)


class QueueManagementService(models.Model):
    _name = 'queue.management.service'
    name = fields.Char(required=True, string='Service Name')
    state = fields.Selection([
            ('opened', 'Opened'),
            ('closed', 'Closed')], 'Service status', required=True, copy=False, default='closed')
    branch_id = fields.Many2one('queue.management.branch', 'Branch', required=True)
    sequence_id = fields.Many2one('ir.sequence', string='Letter', required=True)


class QueueManagementAgent(models.Model):
    _name = 'queue.management.agent'
    _inherits = {'res.users': 'user_id'}
    user_id = fields.Many2one('res.users')
    desk = fields.Selection([(k, v) for k, v in number_of_desks.items()],
                            'Desk', required=True, copy=False, default='1')
    primary_service_id = fields.Many2one('queue.management.service', string="Primary service")

    @api.model
    def default_get(self, fields_list):
        result = super(QueueManagementAgent, self).default_get(fields_list)
        result['groups_id'] = [(4, self.env.ref('queue_management.group_queue_management_branch_agent').id, 0)]
        return result
