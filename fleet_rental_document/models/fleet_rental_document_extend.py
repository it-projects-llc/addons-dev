# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import openerp.addons.decimal_precision as dp


class FleetRentalDocumentExtend(models.Model):
    _name = 'fleet_rental.document_extend'
    _inherit = 'fleet_rental.document_rent'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('booked', 'Booked'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')

    document_rent_id = fields.Many2one('fleet_rental.document_rent')
    balance = fields.Float(related='document_rent_id.balance', readonly=True)
    advanced_deposit = fields.Float(related='document_rent_id.advanced_deposit', readonly=True)

    @api.model
    def default_get(self, fields_list):
        defaults = super(FleetRentalDocumentExtend, self).default_get(fields_list)
        context = dict(self._context or {})
        active_id = context.get('active_id')
        rent = self.env['fleet_rental.document_rent'].browse(active_id)
        defaults.setdefault('vehicle_id', rent.vehicle_id.id)
        defaults.setdefault('partner_id', rent.partner_id.id)
        defaults['exit_datetime'] = rent.exit_datetime
        defaults['diff_datetime'] = self.env['fleet_rental.document_extend'].search(
                                            [('document_rent_id', '=', rent.id)], limit=1,
                                            order='return_datetime desc').return_datetime or rent.return_datetime
        defaults['return_datetime'] = fields.Datetime.to_string(fields.Datetime.from_string(defaults['diff_datetime']) + timedelta(days=1))
        defaults.setdefault('rate_per_extra_km', rent.rate_per_extra_km)
        defaults.setdefault('extra_driver_charge_per_day', rent.extra_driver_charge_per_day)
        defaults.setdefault('odometer_before', rent.odometer_before)
        defaults.setdefault('daily_rental_price', rent.daily_rental_price)
        defaults.setdefault('allowed_kilometer_per_day', rent.allowed_kilometer_per_day)
        defaults.setdefault('partner_id', rent.partner_id)
        return defaults

    @api.multi
    def action_submit(self):
        for rent in self:
            rent.state = 'booked'
            self.vehicle_id.state_id = self.env.ref('fleet.vehicle_state_booked')

    @api.multi
    def action_view_invoice(self):
        return self.mapped('document_id').action_view_invoice()
