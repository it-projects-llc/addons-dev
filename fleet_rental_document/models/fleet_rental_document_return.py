# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import openerp.addons.decimal_precision as dp


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

    odometer_after = fields.Float(string='Odometer after Rent', related='vehicle_id.odometer')

    extra_hours = fields.Integer(string='Extra Hours', compute="_compute_extra_hours", store=True, readonly=True, default=0)
    extra_kilometers = fields.Float(string='Extra Kilometers', compute="_compute_extra_kilometers", store=True, readonly=True, default=0)

    discount = fields.Float(string='Discount', digits_compute=dp.get_precision('Product Price'), default=0)
    penalties = fields.Float(string='Penalties', digits_compute=dp.get_precision('Product Price'), default=0)
    extra_hours_charge = fields.Float(string='Extra Hours Charge', digits_compute=dp.get_precision('Product Price'), compute="_compute_extra_hours", store=True, readonly=True, default=0)
    extra_kilos_charge = fields.Float(string='Extra Kilos Charge', digits_compute=dp.get_precision('Product Price'), compute="_compute_extra_kilometers", store=True, readonly=True, default=0)
    price_after_discount = fields.Float(string='Price After Discount', compute="_compute_price_after_discount", store=True, digits_compute=dp.get_precision('Product Price'), readonly=True)

    @api.multi
    @api.depends('period_rent_price', 'extra_driver_charge', 'other_extra_charges')
    def _compute_total_rent_price(self):
        for record in self:
            record.total_rent_price = record.period_rent_price + record.extra_driver_charge + record.other_extra_charges

    @api.onchange('period_rent_price', 'extra_driver_charge', 'other_extra_charges', 'extra_hours_charge', 'extra_kilos_charge', 'penalties')
    def _onchange_total_price_fields(self):
        self.total_rent_price = self.period_rent_price + self.extra_driver_charge + self.other_extra_charges + \
                                self.extra_hours_charge + self.extra_kilos_charge + self.penalties

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

    @api.multi
    @api.depends('exit_datetime', 'return_datetime')
    def _compute_extra_hours(self):
        for record in self:
            if record.exit_datetime and record.return_datetime:
                start = datetime.strptime(record.exit_datetime, DTF)
                end = datetime.strptime(record.return_datetime, DTF)
                extra_hours = (end - start).seconds // 3600
                record.extra_hours = (end - start).seconds // 3600
                record.extra_hours_charge = (record.daily_rental_price / 24) * extra_hours

    @api.multi
    @api.depends('vehicle_id.odometer', 'document_id.total_rental_period', 'odometer_after')
    def _compute_extra_kilometers(self):
        for record in self:
            if record.odometer_after and record.total_rental_period and record.allowed_kilometer_per_day:
                kilometers_diff = record.odometer_after - record.odometer_before - (record.total_rental_period * record.allowed_kilometer_per_day)
                extra_kilometers = kilometers_diff if kilometers_diff > 0 else 0
                record.extra_kilometers = extra_kilometers
                record.extra_kilos_charge = extra_kilometers * record.rate_per_extra_km

    @api.multi
    @api.depends('total_rent_price', 'discount')
    def _compute_price_after_discount(self):
        for record in self:
            record.price_after_discount = record.total_rent_price - record.discount

    @api.multi
    @api.depends('price_after_discount', 'advanced_deposit')
    def _compute_balance(self):
        for record in self:
            record.balance = record.price_after_discount - record.advanced_deposit

    @api.onchange('price_after_discount')
    def _onchange_price_after_discount(self):
        self.balance = self.price_after_discount - self.advanced_deposit

    @api.onchange('return_datetime')
    def _onchange_return_datetime(self):
        if self.exit_datetime and self.return_datetime:
            start = datetime.strptime(self.exit_datetime, DTF)
            end = datetime.strptime(self.return_datetime, DTF)
            self.total_rental_period = (end - start).days
            self.period_rent_price = self.total_rental_period * self.daily_rental_price

    @api.onchange('odometer_before', 'odometer_after', 'total_rental_period')
    def _onchange_period_or_odometer(self):
        kilometers_diff = self.odometer_after - self.odometer_before - (self.total_rental_period * self.allowed_kilometer_per_day)
        self.extra_kilometers = kilometers_diff if kilometers_diff > 0 else 0
