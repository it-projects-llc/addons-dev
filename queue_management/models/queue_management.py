# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _

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
    ticket_id = fields.Many2one('queue.management.ticket', 'Ticket')
    desk = fields.Selection([(k, v) for k, v in number_of_desks.items()],
                            'Desk', required=True, copy=False, default='1')
    service_id = fields.Many2one('queue.management.service', 'Service', related='ticket_id.service_id')
    ticket_state = fields.Selection(string='Ticket State', related='ticket_id.ticket_state', readonly=True)


class QueueManagementTicket(models.Model):
    _name = 'queue.management.ticket'
    name = fields.Char(string='Ticket Name', readonly=True)
    service_id = fields.Many2one('queue.management.service', 'Service', required='True')
    ticket_state = fields.Selection([
        ('pending', 'Pending'),
        ('previous', 'Previous'),
        ('current', 'Current'),
        ('next', 'Next'),
        ('done', 'Done'),
        ('no-show', 'No-show')], 'Ticket State', required=True, copy=False, default='pending')#readonly

    def _generate_order_by(self, order_spec, query):
        my_order = "CASE WHEN ticket_state='current'  THEN 0   WHEN ticket_state = 'next'  THEN 1 WHEN ticket_state = 'pending'  THEN 2 END"
        if order_spec:
            return super(QueueManagementTicket, self)._generate_order_by(order_spec, query) + ", " + my_order
        return " order by " + my_order

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            service = self.env['queue.management.service'].browse(vals.get('service_id'))
            vals['name'] = service.sequence_id.next_by_id()
        if not self.is_next_exist(vals['service_id']):
            vals['ticket_state'] = 'next'
        return super(QueueManagementTicket, self).create(vals)

    @api.multi
    def change_state_done(self):
        for record in self:
            record.ticket_state = 'done'
        return{
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'queue.management.ticket',
            }

    @api.multi
    def change_state_no_show(self):
        for record in self:
            record.ticket_state = 'no-show'

    @api.model
    def is_next_exist(self, service_id):
        return self.search_count([('ticket_state', '=', 'next')])

    @api.model
    def get_next_ticket(self, service_id):
        next_ticket = self.search([('ticket_state', '=', 'pending'),
                                   ('service_id', '=', service_id)], limit=1, order='name')
        if self.is_next_exist(service_id):
            return None
        return next_ticket

    @api.multi
    def call_client(self):
        self.ensure_one()
        agent = self.env['queue.management.agent'].sudo().search([('user_id', '=', self.env.uid)])
        current = self.search([('ticket_state', '=', 'current'),
                               ('service_id', 'in', agent.service_ids.mapped('id') + agent.primary_service_id.mapped('id'))])
        if current:
            raise UserError(_('You already have current ticket, make it done first.'))
        else:
            self.ticket_state = 'current'
            self.env['queue.management.log'].create({'ticket_id': self.id,
                                                     'desk': agent.desk,})
            ticket = self.get_next_ticket(agent.primary_service_id.id)
            if ticket:
                ticket.ticket_state = 'next'
                self.env['queue.management.log'].create({'ticket_id': ticket.id,
                                                         'desk': agent.desk,})
            return{
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'queue.management.ticket',
            }


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
    primary_service_id = fields.Many2one('queue.management.service',
                                         string="Primary service", required=True,
                                         domain="[('id', 'in', service_ids[0][2])]")
    service_ids = fields.Many2many('queue.management.service', string="Services")

    @api.model
    def default_get(self, fields_list):
        result = super(QueueManagementAgent, self).default_get(fields_list)
        result['groups_id'] = [(4, self.env.ref('queue_management.group_queue_management_branch_agent').id, 0)]
        return result


class QueueManagementManager(models.Model):
    _name = 'queue.management.manager'
    _inherits = {'res.users': 'user_id'}
    user_id = fields.Many2one('res.users')

    @api.model
    def default_get(self, fields_list):
        result = super(QueueManagementManager, self).default_get(fields_list)
        result['groups_id'] = [(4, self.env.ref('queue_management.group_queue_management_branch_manager').id, 0)]
        return result
