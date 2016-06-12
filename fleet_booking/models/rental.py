# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from openerp.osv import fields


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
    membership_type = fields.Char(string='Membership Type', related='partner_id.type_id.name', store=False, readonly=True)

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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    _display_name_store_triggers = {
        'res.partner': (lambda self, cr, uid, ids, context=None: self.search(cr, uid,
                        [('id', 'child_of', ids)], context=dict(active_test=False)),
                        ['parent_id', 'is_company', 'name', 'id'], 10)
        }

    _display_name = lambda self, *args, **kwargs: self._display_name_compute(*args, **kwargs)
    _columns = {
        'display_name': fields.function(_display_name, type='char', string='Name',
                                        store=_display_name_store_triggers, select=True)
        }

    def name_get(self, cr, uid, ids, context=None):
        result = dict(super(ResPartnerPhone, self).name_get(cr, uid, ids, context=None))
        records = self.browse(cr, uid, result.keys(), context)
        for r in records:
            if r.id:
                result[r.id] = result[r.id] + ' (' + r.id+ ')'
        return result.items()
