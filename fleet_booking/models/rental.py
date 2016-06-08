# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api

class FleetBookingDocument(models.Model):
    _name = 'fleet_booking.document'

    name = fields.Char(string='Document Reference', required=True, copy=False, readonly=True, index=True, default='New')

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('booked', 'Booked'),
        ('confirmed', 'Confirmed'),
        ('extended', 'Extended'),
        ('cancel', 'Cancelled'),
        ('return_draft', 'Return Draft'),
        ('return_open', 'Return Open'),
        ('return_closed', 'Return Closed'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')

    type = fields.Selection([
            ('rent','Rent'),
            ('extended_rent','Extended Rent'),
            ('return','Return'),
        ], readonly=True, index=True, change_default=True)


    origin = fields.Char(string='Source Document',
        help="Reference of the document that produced this document.",
        readonly=True, states={'draft': [('readonly', False)]})


class FleetBookingRentDocument(models.Model):
    _name = 'fleet_booking.rent_document'

    _inherits = {
                 'fleet_booking.document': 'document_id',
                 }

    document_id = fields.Many2one('fleet_booking.document', required=True,
            string='Related Document', ondelete='restrict',
            help='common part of all three types of the documents', auto_join=True)
