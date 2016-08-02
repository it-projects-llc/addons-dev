# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import openerp.addons.decimal_precision as dp
import base64
from lxml import etree
import os
from wand.image import Image


class FleetRentalDocumentRent(models.Model):
    _name = 'fleet_rental.document_rent'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('booked', 'Booked'),
        ('confirmed', 'Confirmed'),
        ('extended', 'Extended'),
        ('returned', 'Returned'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')
    _inherits = {
                 'fleet_rental.document': 'document_id',
                 }

    document_id = fields.Many2one('fleet_rental.document', required=True,
            string='Related Document', ondelete='restrict',
            help='common part of all three types of the documents', auto_join=True)

    additional_driver_ids = fields.Many2many('fleet_rental.additional_driver')
    user_branch_id = fields.Many2one('fleet_branch.branch', default=lambda self: self.env.user.branch_id.id)

    document_return_id = fields.Many2one('fleet_rental.document_return')

    document_extend_ids = fields.One2many('fleet_rental.document_extend', 'document_rent_id')
    extends_count = fields.Integer(string='# of Extends', compute='_get_extends', readonly=True)
    diff_datetime = fields.Datetime(string='Previous rent document return date and time')

    odometer_before = fields.Float(string='Odometer', compute='_compute_odometer', store=True, readonly=True)

    @api.model
    def default_get(self, fields_list):
        result = super(FleetRentalDocumentRent, self).default_get(fields_list)
        items = self.env['fleet_rental.item_to_check'].search([])
        parts = self.env['fleet_rental.svg_vehicle_part'].search([])

        result['check_line_ids'] = [(5, 0, 0)] + [(0, 0, {'item_id': item.id,'exit_check_yes': False, 'exit_check_no': False,'exit_check_yes': False, 'exit_check_no': False,}) for item in items]
        result['part_line_ids'] = [(5, 0, 0)] + [(0, 0, {'part_id': part.id, 'path_ID': part.path_ID}) for part in parts]
        result['exit_datetime'] = fields.Datetime.now()
        result['return_datetime'] = fields.Datetime.to_string(datetime.utcnow() + timedelta(days=1))
        return result

    @api.onchange('total_rent_price', 'advanced_deposit')
    def _compute_balance(self):
        for record in self:
            record.balance = record.total_rent_price - record.advanced_deposit

    @api.onchange('exit_datetime', 'return_datetime')
    def _compute_total_rental_period(self):
        for record in self:
            if record.exit_datetime and record.return_datetime:
                start = datetime.strptime(record.exit_datetime.split()[0], DEFAULT_SERVER_DATE_FORMAT)
                end = datetime.strptime(record.return_datetime.split()[0], DEFAULT_SERVER_DATE_FORMAT)
                record.total_rental_period = (end - start).days

    @api.onchange('daily_rental_price', 'total_rental_period')
    def _compute_period_rent_price(self):
        for record in self:
            record.period_rent_price = record.total_rental_period * record.daily_rental_price

    @api.onchange('total_rental_period', 'extra_driver_charge_per_day')
    def _compute_extra_driver_charge(self):
        for record in self:
            if record.total_rental_period:
                record.extra_driver_charge = record.total_rental_period * record.extra_driver_charge_per_day

    @api.onchange('period_rent_price', 'extra_driver_charge', 'other_extra_charges')
    def _compute_total_rent_price(self):
        for record in self:
            record.total_rent_price = record.period_rent_price + record.extra_driver_charge + record.other_extra_charges

    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        for record in self:
            record.allowed_kilometer_per_day = record.vehicle_id.allowed_kilometer_per_day
            record.rate_per_extra_km = record.vehicle_id.rate_per_extra_km
            record.daily_rental_price = record.vehicle_id.daily_rental_price

    @api.depends('vehicle_id')
    def _compute_odometer(self):
        for record in self:
            record.odometer_before = record.vehicle_id.odometer

    @api.depends('document_extend_ids')
    def _get_extends(self):
        for document in self:
            document.update({
                'extends_count': len(document.document_extend_ids),
            })

    @api.multi
    def action_view_invoice(self):
        return self.mapped('document_id').action_view_invoice()

    @api.depends('invoice_line_ids')
    def _get_invoiced(self):
        for document in self:
            invoice_ids = document.invoice_line_ids.mapped('invoice_id')
            # Search for refunds as well
            refund_ids = self.env['account.invoice'].browse()
            if invoice_ids:
                refund_ids = refund_ids.search([('type', '=', 'out_refund'), ('origin', 'in', invoice_ids.mapped('number')), ('origin', '!=', False)])

            document.update({
                'invoice_count': len(set(invoice_ids.ids + refund_ids.ids)),
                'invoice_ids': invoice_ids.ids + refund_ids.ids,
            })

    @api.multi
    def action_book(self):
        for rent in self:
            rent.state = 'booked'
            self.vehicle_id.state_id = self.env.ref('fleet.vehicle_state_booked')

    @api.multi
    def action_cancel_booking(self):
        for rent in self:
            rent.state = 'cancel'
            self.vehicle_id.state_id = self.env.ref('fleet.vehicle_state_active')

    @api.multi
    def action_confirm(self):
        for rent in self:
            rent.state = 'confirmed'

    @api.multi
    def action_create_return(self):
        document_return_obj = self.env['fleet_rental.document_return']
        for rent in self:
            document_return = document_return_obj.create({
                'partner_id': rent.partner_id.id,
                'vehicle_id': rent.vehicle_id.id,
                'allowed_kilometer_per_day': rent.allowed_kilometer_per_day,
                'rate_per_extra_km': rent.rate_per_extra_km,
                'daily_rental_price': rent.daily_rental_price,
                'origin': rent.name,
                'exit_datetime': rent.exit_datetime,
                'type': 'return',
                'return_datetime': fields.Datetime.now(),
                'odometer_before': rent.odometer_before,
                'rent_return_datetime': rent.return_datetime,
                'extra_driver_charge_per_day': rent.extra_driver_charge_per_day,
                'extra_driver_charge': rent.extra_driver_charge,
                'document_rent_id': rent.id,
                'other_extra_charges': rent.other_extra_charges,
                'check_line_ids': [(6, 0, rent.check_line_ids.ids)],
                'part_line_ids': [(6, 0, rent.part_line_ids.ids)],
                'advanced_deposit': rent.advanced_deposit,
               })
            rent.sudo().write({'document_return_id': document_return.id})

        return self.action_view_document_return(document_return.id)

    @api.multi
    def action_view_document_return(self, document_return_id):
        action = self.env.ref('fleet_rental_document.fleet_rental_return_document_draft_act')
        form_view_id = self.env.ref('fleet_rental_document.fleet_rental_return_document_form').id

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [(form_view_id, 'form')],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        result['res_id'] = document_return_id
        return result

    @api.multi
    def action_view_document_extend(self, document_return_id):
        action = self.env.ref('fleet_rental_document.fleet_rental_document_extend_act')
        form_view_id = self.env.ref('fleet_rental_document.fleet_rental_document_extend_form').id

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [(form_view_id, 'form')],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        result['res_id'] = document_return_id
        return result

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet_rental.document_rent') or 'New'
        result = super(FleetRentalDocumentRent, self).create(vals)
        return result

    @api.multi
    def print_rent(self):
        return self.env['report'].get_action(self, 'fleet_rental_document.report_rent')
