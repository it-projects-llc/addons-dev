# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api


class FleetBookingDocument(models.Model):
    _name = 'fleet_booking.document'

    name = fields.Char(string='Agreement Number', required=True, copy=False, readonly=True, index=True, default='New')

    type = fields.Selection([
            ('rent','Rent'),
            ('extended_rent','Extended Rent'),
            ('return','Return'),
        ], readonly=True, index=True, change_default=True)

    origin = fields.Char(string='Source Document',
        help="Reference of the document that produced this document.",
        readonly=True, states={'draft': [('readonly', False)]})

    partner_id = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)])
    customer_name = fields.Char(string='Customer name', related="partner_id.name", store=False)
    customer_ID = fields.Integer(string='Customer ID', related='partner_id.id', store=False)
    customer_membership_number = fields.Integer(string='Customer membership number', related='partner_id.id', store=False)
    membership_type = fields.Char(string='Membership Type', related='partner_id.type_id.name', store=False)

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")

    exit_checked_item_ids = fields.Many2many('fleet_booking.item_to_be_checked', 'document_exit_checking_items_rel', 'document_id', 'item_id', copy=False, string='On Exit')


class FleetBookingRent(models.Model):
    _name = 'fleet_booking.rent'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('booked', 'Booked'),
        ('confirmed', 'Confirmed'),
        ('extended', 'Extended'),
        ('returned', 'Returned'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')

    _inherits = {
                 'fleet_booking.document': 'document_id',
                 }

    document_id = fields.Many2one('fleet_booking.document', required=True,
            string='Related Document', ondelete='restrict',
            help='common part of all three types of the documents', auto_join=True)


class FleetBookingReturn(models.Model):
    _name = 'fleet_booking.return'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Returned but Open'),
        ('closed', 'Returned and Closed'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')

    _inherits = {
                 'fleet_booking.document': 'document_id',
                 }

    document_id = fields.Many2one('fleet_booking.document', required=True,
            string='Related Document', ondelete='restrict',
            help='common part of all three types of the documents', auto_join=True)


class FleetBookingItemsToBeChecked(models.Model):
    _name = 'fleet_booking.item_to_be_checked'

    name = fields.Char(string='Item', help='Item to be checked before and after rent')
