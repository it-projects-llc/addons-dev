# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api


class FleetRentalDocumentReturn(models.Model):
    _name = 'fleet_rental.document_return'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')

    _inherits = {
                 'fleet_rental.document': 'document_id',
                 }

    document_id = fields.Many2one('fleet_rental.document', required=True,
            string='Related Document', ondelete='restrict',
            help='common part of all three types of the documents', auto_join=True)

    document_rent_id = fields.Many2one('fleet_rental.document_rent', required=True,
            string='Related Rent Document', ondelete='restrict',
            help='Source Rent document')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet_rental.document_return') or 'New'
        result = super(FleetRentalDocumentReturn, self).create(vals)
        return result

    @api.multi
    def action_open(self):
        for rent in self:
            rent.state = 'open'



