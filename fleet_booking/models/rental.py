# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api


class FleetBookingRental(models.Model):
    _name = 'fleet_booking.rental'

    name = fields.Char(string='Document Reference', required=True, copy=False, readonly=True, index=True, default='New')

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('booked', 'Booked'),
        ('sale', 'Sale Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
 
