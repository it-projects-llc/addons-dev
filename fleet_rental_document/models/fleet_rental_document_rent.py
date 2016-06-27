# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api


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

    document_return_ids = fields.One2many('fleet_rental.document_return', 'document_rent_id', string='Return documents', copy=False)
    user_branch_id = fields.Many2one('fleet_branch.branch', default=lambda self: self.env.user.branch_id.id)

    @api.multi
    def action_view_invoice(self):
        return self.mapped('document_id').action_view_invoice()

    @api.multi
    def action_book(self):
        for rent in self:
            rent.state = 'booked'
            vehicle = self.env['fleet.vehicle'].browse(rent.vehicle_id.id)
            booked_vehicle_state = self.env['fleet.vehicle.state'].browse(6)
            vehicle.state_id = booked_vehicle_state

    @api.multi
    def action_cancel_booking(self):
        for rent in self:
            rent.state = 'cancel'
            self.set_vehicle_active(rent)

    @api.multi
    def action_confirm(self):
        for rent in self:
            rent.state = 'confirmed'

    @api.multi
    def action_create_return(self):
        document_return_obj = self.env['fleet_rental.document_return']
        for rent in self:
            rent.state = 'returned'
            self.set_vehicle_active(rent)
            document_return = document_return_obj.create({
               'partner_id': rent.partner_id.id,
               'vehicle_id': rent.vehicle_id.id,
               'allowed_kilometer_per_day': rent.allowed_kilometer_per_day,
               'rate_per_extra_km': rent.rate_per_extra_km,
               'daily_rental_price': rent.daily_rental_price,
               'document_rent_id': rent.id,
               'origin': rent.name,
               'exit_datetime': rent.exit_datetime,
               'odometer_before': rent.odometer_before,
               })
        return self.action_view_document_return()

    @api.multi
    def action_view_document_return(self):
        document_return_ids = self.mapped('document_return_ids')[0]
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
        if len(document_return_ids) == 1:
            # TODO: think about what if there would be more than one return documents
            result['res_id'] = document_return_ids.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet_rental.document_rent') or 'New'
        result = super(FleetRentalDocumentRent, self).create(vals)
        return result

    def set_vehicle_active(self, rec):
        vehicle = self.env['fleet.vehicle'].browse(rec.vehicle_id.id)
        active_vehicle_state = self.env['fleet.vehicle.state'].browse(2)
        vehicle.state_id = active_vehicle_state

