# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api


class FleetBookingDocumentRent(models.Model):
    _name = 'fleet_booking.document_rent'

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
