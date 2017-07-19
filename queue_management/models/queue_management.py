# -*- coding: utf-8 -*-

from odoo import models, fields, api


class queue_management_information(models.Model):
    _name = 'queue.management.info'
    company_name = fields.Char(required=True, string="Company Name")
    industry = fields.Selection([('telecoms', 'Telecoms'),
                                 ('public_services', 'Public Services'),
                                 ('banks', 'Banks'),
                                 ('clinics', 'Hospitals/Clinics'),
                                 ('utilities', 'Utilities'),
                                 ('insurance', 'Insurance'),
                                 ('education', 'Education'),
                                 ('service_center', 'Service Centers'),
                                 ('travel', 'Travel'),
                                 ('automotive', 'Automotive')], 'Industry', required=True, copy=False)
    number_of_branches = fields.Integer(required=True, string="N.Branches")
    address = fields.Char(required=True, string="Address")
    postal_code = fields.Char(required=True, string="Postal Code")
    region = fields.Char(required=True, string="State/Region")
    city = fields.Char(required=True, string="City")


class queue_management_branch(models.Model):
    _name = 'queue.management.branch'
    name = fields.Char(required=True, string="Branch Name")
    service_ids = fields.One2many('queue.management.service', 'branch_id', required=True)
    user_ids = fields.One2many('queue.management.user', 'user_id')


class queue_management_user(models.Model):
    _name = 'queue.management.user'
    position_id = fields.Many2one('res.groups', 'Position')
    desk = fields.Selection([('1', '1'),
                             ('2', '2')], 'Desk Number', required=True, copy=False, default='1')
    primary_service_id = fields.Many2one('queue.management.service')
    user_id = fields.Many2one('queue.management.branch', 'User')


class queue_management_screen(models.Model):
    _name = 'queue.management.screen'
    ticket_id = fields.Many2one('queue.management.ticket', 'Ticket number')
    desk_id = fields.Many2one('queue.magment.user', 'Desk', domain='')# не знаю пока какие условия для домена делать
    service_id = fields.Many2one('queue.management.service', 'Service')
    state = fields.Selection([
        ('previous', 'Previous'),
        ('current', 'Current'),
        ('next', 'Next'),
        ('done', 'Done'),
        ('no-show', 'No-show')], 'Ticket State', required=True, copy=False, default='next')


class queue_management_ticket(models.Model):
    _name = 'queue.management.ticket'
    name = fields.Char(required=True, string='Ticket Name')
    ticket_id = fields.Many2one('queue.management.service', 'Ticket')


class queue_management_service(models.Model):
    _name = 'queue.management.service'
    name = fields.Char(required=True, string='Service Name')
    state = fields.Selection([
            ('opened', 'Opened'),
            ('closed', 'Closed'),
    ], 'Service status', required=True, copy=False, default='closed')
    branch_id = fields.Many2one('queue.management.branch', 'Branch', required=True)
    letter = fields.Char(required=True, string="Service Letter")
