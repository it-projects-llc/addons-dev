# -*- coding: utf-8 -*-

from odoo import models, fields, api


Industries = {'telecoms': 'Telecoms',
              'public_services': 'Public Services',
              'banks': 'Banks',
              'clinics': 'Hospitals/Clinics',
              'utilities': 'Utilities',
              'insurance': 'Insurance',
              'education': 'Education',
              'service_center': 'Service Centers',
              'travel': 'Travel',
              'automotive': 'Automotive'}
SERVICE_STATUS = {'opened': 'Opened',
                  'closed': 'Closed'}
ticket_state = {'previous': 'Previous',
                'current': 'Current',
                'next': 'Next',
                'done': 'Done',
                'no-show': 'No-show'}
desk_number = {'1': '1',
               '2': '2',
               '3': '3'}


class queue_management_information(models.Model):
    _name = 'queue.manag.info'
    company_name = fields.Char(required=True, string="Company Name")
    industry = fields.Selection([(k, v) for k, v in Industries.items()],
                             'Industry', required=True, copy=False)
    number_of_branches = fields.Integer(required=True, string="N.Branches")
    address = fields.Char(required=True, string="Address")
    postal_code = fields.Char(required=True, string="Postal Code")
    region = fields.Char(required=True, string="State/Region")
    city = fields.Char(required=True, string="City")


class queue_management_branch(models.Model):
    _name = 'queue.management.branch'
    name = fields.Char(required=True, string="Branch Name")
    service = fields.One2many('queue.management.service', 'Services', required=True)
    user_ids = fields.One2many('queue.management.user', 'User')


class queue_management_user(models.Model):
    _name = 'queue.management.user'
    position = fields.Many2one('res.groups', 'Position')
    desk = fields.Many2one()#???
    desk = fields.Selection([(k, v) for k, v in desk_number.items()],
                                      'Desk Number', required=True, copy=False, default='1')
    primary_serviced = fields.Many2one('queue.management.service')


class queue_management_screen(models.Model):
    _name = 'queue.management.screen'
    ticket = fields.Many2one('queue.management.ticket', 'Ticket number')
    desk = fields.Many2one('queue.magment.user', 'Desk')
    service = fields.Many2one('queue.management.service', 'Service')
    state = fields.Selection([(k, v) for k, v in ticket_state.items()],
                                      'Ticket State', required=True, copy=False, default='next')


class queue_management_ticket(models.Model):
    _name = 'queue.management.ticket'
    number = fields.Many2one('queue.management.user', 'Ticket')


class queue_management_service(models.Model):
    _name = 'queue.management.service'
    name = fields.Char(required=True, string='Service Name')
    state = fields.Selection([(k, v) for k, v in SERVICE_STATUS.items()],
                                      'Service status', required=True, copy=False, default='closed')
    branch = fields.Many2one('queue.management.branch', 'Branch', required=True)
    letter = fields.Char(required=True, string="Service Letter")
