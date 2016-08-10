# -*- coding: utf-8 -*-
from openerp import models, fields, api


class FleetRentalCreateDocumentWizard(models.TransientModel):
    _name = "fleet_rental.create_document_wizard"

    @api.model
    def _default_document_model(self):
        return self._context.get('default_model')

    document_rent = fields.Many2one('fleet_rental.document_rent', string='Agreement Number',
                                       domain = lambda self: [('vehicle_id.branch_id', '=', self.env.user.branch_id.id), ('state', 'in', ['confirmed', 'extended'])])
    vehicle = fields.Many2one('fleet.vehicle', string='Car Plate',
                                domain = lambda self: [('branch_id', '=', self.env.user.branch_id.id), ('state_id', '=', self.env.ref('fleet_rental_document.vehicle_state_booked').id)])

    document_model = fields.Char(default=_default_document_model)


    @api.onchange('document_rent')
    def _onchange_document_rent(self):
        self.vehicle = self.document_rent.vehicle_id

    @api.onchange('vehicle')
    def _onchange_vehicle(self):
        if self.vehicle:
            self.document_rent = self.env['fleet_rental.document_rent'].search([('vehicle_id', '=', self.vehicle.id)], limit=1)

    @api.multi
    def action_create(self):
        if self.document_model == 'fleet_rental.document_return':
            return self.document_rent.action_create_return()
        elif self.document_model == 'fleet_rental.document_extend':
            return self.document_rent.action_extend()
