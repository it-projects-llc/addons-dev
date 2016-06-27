# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


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

    odometer_after = fields.Float(string='Odometer after Rent', related='vehicle_id.odometer')

    extra_hours = fields.Integer(string='Extra Hours', compute="_compute_extra_hours", store=True, readonly=True)

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

    @api.depends('exit_datetime', 'return_datetime')
    def _compute_extra_hours(self):
        for record in self:
            if record.exit_datetime and record.return_datetime:
                start = datetime.strptime(record.exit_datetime, DTF)
                end = datetime.strptime(record.return_datetime, DTF)
                record.total_rental_period = (end - start).hours

