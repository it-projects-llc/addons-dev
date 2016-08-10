# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import openerp.addons.decimal_precision as dp


class FleetRentalDocumentReturn(models.Model):
    _name = 'fleet_rental.document_return'
    _inherits = {'fleet_rental.document': 'document_id',
                 'fleet_rental.document_rent': 'document_rent_id',}

    document_id = fields.Many2one('fleet_rental.document', required=True,
                                  ondelete='restrict', auto_join=True)
    document_rent_id = fields.Many2one('fleet_rental.document_rent',
                                       ondelete='restrict', required=True, auto_join=True)
    name = fields.Char(string='Agreement Number', required=True,
                       copy=False, readonly=True, index=True, default='New')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')
    type = fields.Selection([
        ('rent', 'Rent'),
        ('extend', 'Extend'),
        ('return', 'Return'),
        ], readonly=True, index=True, change_default=True)
    origin = fields.Char(string='Source Document',
                         help="Reference of the document that produced this document.",
                         readonly=True, states={'draft': [('readonly', False)]})
    invoice_count = fields.Integer(string='# of Invoices', related='document_id.invoice_count',
                                   readonly=True)
    rental_account_id = fields.Many2one('account.analytic.account',
                                        string='analytic account for rental', readonly=True,
                                        related='document_id.rental_account_id')
    advanced_deposit = fields.Float(string='Advanced Deposit',
                                    digits_compute=dp.get_precision('Product Price'), readonly=True)
    balance = fields.Float(string='Balance', compute="_compute_balance", store=True,
                           digits_compute=dp.get_precision('Product Price'), readonly=True)
    total_rent_price = fields.Float(string='Total Rent Price', compute="_compute_total_rent_price",
                                    store=True, digits_compute=dp.get_precision('Product Price'),
                                    readonly=True)
    customer_shall_pay = fields.Float(string='Customer Shall Pay',
                                      compute="_compute_customer_shall_pay",
                                      store=True, digits_compute=dp.get_precision('Product Price'),
                                      readonly=True)
    returned_amount = fields.Float(string='Returned Amount', compute="_compute_returned_amount",
                                   store=True, digits_compute=dp.get_precision('Product Price'),
                                   readonly=True)
    paid_amount = fields.Float(string='Paid Amount', related="document_id.paid_amount",
                               digits_compute=dp.get_precision('Product Price'), readonly=True)
    diff_pa_csp = fields.Float(compute="_compute_diff_pa_csp")
    odometer_after = fields.Float(string='Odometer after Rent', related='vehicle_id.odometer')
    return_datetime = fields.Datetime(string='Return Date and Time', required=True,
                                      default=fields.Datetime.now)
    total_rental_period = fields.Integer(string='Total Rental Period',
                                         compute="_compute_total_rental_period",
                                         store=True, readonly=True)
    period_rent_price = fields.Float(string='Period Rent Price',
                                     compute="_compute_period_rent_price", store=True,
                                     digits_compute=dp.get_precision('Product Price'),
                                     readonly=True)
    extra_driver_charge = fields.Float(string='Extra Driver Charge',
                                       compute="_compute_extra_driver_charge", store=True,
                                       digits_compute=dp.get_precision('Product Price'),
                                       readonly=True)
    extra_hours = fields.Integer(string='Extra Hours', compute="_compute_extra_hours", store=True,
                                 readonly=True, default=0)
    extra_kilometers = fields.Float(string='Extra Kilometers', compute="_compute_extra_kilometers",
                                    store=True, readonly=True, default=0)
    discount = fields.Float(string='Discount', digits_compute=dp.get_precision('Product Price'),
                            default=0)
    penalties = fields.Float(string='Penalties', digits_compute=dp.get_precision('Product Price'),
                             default=0)
    extra_hours_charge = fields.Float(string='Extra Hours Charge',
                                      digits_compute=dp.get_precision('Product Price'),
                                      compute="_compute_extra_hours", store=True, readonly=True,
                                      default=0)
    extra_kilos_charge = fields.Float(string='Extra Kilos Charge',
                                      digits_compute=dp.get_precision('Product Price'),
                                      compute="_compute_extra_kilometers", store=True,
                                      readonly=True, default=0)
    price_after_discount = fields.Float(string='Price After Discount',
                                        compute="_compute_price_after_discount", store=True,
                                        digits_compute=dp.get_precision('Product Price'),
                                        readonly=True)


    @api.one
    @api.depends('return_datetime')
    def _compute_extra_hours(self):
        if self.return_datetime:
            start = datetime.strptime(self.document_rent_id.exit_datetime, DTF)
            end = datetime.strptime(self.return_datetime, DTF)
            days = (end - start).days
            if self.document_rent_id.extend_return_date:
                return_date = datetime.strptime(self.document_rent_id.extend_return_date,
                                                       DEFAULT_SERVER_DATE_FORMAT)
            else:
                return_date = datetime.strptime(self.document_rent_id.return_date,
                                                       DEFAULT_SERVER_DATE_FORMAT)

            exit_date = datetime.strptime(self.exit_datetime.split()[0],
                                             DEFAULT_SERVER_DATE_FORMAT)
            days = days - (return_date - exit_date).days
            extra_hours = days * 24 + (end - start).seconds/3600
            if extra_hours > 0:
                self.extra_hours = extra_hours
                self.extra_hours_charge = (self.daily_rental_price / 24) * extra_hours
            else:
                self.extra_hours = 0
                self.extra_hours_charge = 0

    @api.multi
    @api.depends('vehicle_id.odometer', 'total_rental_period', 'odometer_after')
    def _compute_extra_kilometers(self):
        for record in self:
            if record.odometer_after and record.total_rental_period and record.allowed_kilometer_per_day:
                kilometers_diff = record.odometer_after - record.odometer_before - (record.total_rental_period * record.allowed_kilometer_per_day)
                extra_kilometers = kilometers_diff if kilometers_diff > 0 else 0
                record.extra_kilometers = extra_kilometers
                record.extra_kilos_charge = extra_kilometers * record.rate_per_extra_km
            else:
                record.extra_kilometers = 0
                record.extra_kilos_charge = 0

    @api.multi
    @api.depends('total_rent_price', 'discount')
    def _compute_price_after_discount(self):
        for record in self:
            record.price_after_discount = record.total_rent_price - record.discount

    @api.depends('price_after_discount', 'advanced_deposit')
    def _compute_balance(self):
        for record in self:
            record.balance = record.price_after_discount - record.advanced_deposit

    @api.depends('paid_amount', 'customer_shall_pay')
    def _compute_diff_pa_csp(self):
        for record in self:
            record.diff_pa_csp = record.customer_shall_pay - record.paid_amount

    @api.depends('balance')
    def _compute_returned_amount(self):
        for record in self:
            record.returned_amount = abs(record.balance) if record.balance < 0 else 0

    @api.depends('balance')
    def _compute_customer_shall_pay(self):
        for record in self:
            record.customer_shall_pay = record.balance if record.balance > 0 else 0

    @api.depends('period_rent_price', 'extra_driver_charge', 'other_extra_charges',
                 'extra_hours_charge', 'extra_kilos_charge', 'penalties')
    def _compute_total_rent_price(self):
        for record in self:
            record.total_rent_price = record.period_rent_price + record.extra_driver_charge + \
                                      record.other_extra_charges + record.extra_hours_charge + \
                                      record.extra_kilos_charge + record.penalties

    @api.depends('return_datetime')
    def _compute_total_rental_period(self):
        for record in self:
            if record.exit_datetime and record.return_datetime:
                start = datetime.strptime(record.exit_datetime.split()[0],
                                          DEFAULT_SERVER_DATE_FORMAT)
                end = datetime.strptime(record.return_datetime.split()[0],
                                        DEFAULT_SERVER_DATE_FORMAT)
                record.total_rental_period = (end - start).days

    @api.depends('daily_rental_price', 'total_rental_period')
    def _compute_period_rent_price(self):
        for record in self:
            record.period_rent_price = record.total_rental_period * record.daily_rental_price

    @api.depends('total_rental_period', 'extra_driver_charge_per_day')
    def _compute_extra_driver_charge(self):
        for record in self:
            if record.total_rental_period:
                record.extra_driver_charge = record.total_rental_period * \
                                             record.extra_driver_charge_per_day

    @api.multi
    def action_confirm(self):
        for ret in self:
            ret.state = 'closed'
            ret.document_rent_id.sudo().state = 'returned'
            ret.vehicle_id.state_id = self.env.ref('fleet_rental_document.vehicle_state_active')
            ret.partner_id.points += ret.price_after_discount

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet_rental.document_return') or 'New'
        result = super(FleetRentalDocumentReturn, self).create(vals)
        return result

    @api.multi
    def action_return_car(self):
        for ret in self:
            ret.state = 'open'
            ret.document_rent_id.sudo().state = 'returned'
            ret.vehicle_id.state_id= self.env.ref('fleet_rental_document.vehicle_state_active')

    @api.multi
    def print_return(self):
        return self.env['report'].get_action(self, 'fleet_rental_document.report_return')

    @api.multi
    def action_view_invoice(self):
        return self.mapped('document_id').action_view_invoice()
