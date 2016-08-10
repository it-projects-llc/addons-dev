# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import openerp.addons.decimal_precision as dp


class FleetRentalDocumentExtend(models.Model):
    _name = 'fleet_rental.document_extend'
    _inherits = {'fleet_rental.document_rent': 'document_rent_id',
                 'fleet_rental.document': 'document_id'}

    document_id = fields.Many2one('fleet_rental.document', required=True,
                                  ondelete='restrict', auto_join=True)
    document_rent_id = fields.Many2one('fleet_rental.document_rent',
                                       ondelete='restrict', auto_join=True, required=True)

    name = fields.Char(string='Agreement Number', required=True,
                       copy=False, readonly=True, index=True, default='New')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
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
    extra_driver_charge_per_day = fields.Float(string='Extra Driver Charge per day',
                                               digits_compute=dp.get_precision('Product Price'),
                                               default=0)
    extra_driver_charge = fields.Float(string='Extra Driver Charge',
                                       compute="_compute_extra_driver_charge", store=True,
                                       digits_compute=dp.get_precision('Product Price'),
                                       readonly=True)
    new_return_date = fields.Date(string='New Return Date', required=True,
                                  default=fields.Date.context_today)

    total_rental_period = fields.Integer(string='Total Rental Period',
                                         compute="_compute_total_rental_period",
                                         store=True, readonly=True)
    period_rent_price = fields.Float(string='Period Rent Price',
                                     compute="_compute_period_rent_price", store=True,
                                     digits_compute=dp.get_precision('Product Price'),
                                     readonly=True)
    other_extra_charges = fields.Float(string='Other Extra Charges',
                                       digits_compute=dp.get_precision('Product Price'), default=0)
    total_rent_price = fields.Float(string='Total Rent Price', compute="_compute_total_rent_price",
                                    store=True, digits_compute=dp.get_precision('Product Price'),
                                    readonly=True)
    previous_deposit = fields.Float(string='Previous Deposit',
                                    related="document_rent_id.advanced_deposit",
                                    store=True, digits_compute=dp.get_precision('Product Price'),
                                    readonly=True)
    new_deposit = fields.Float(string='New Deposit', related="document_id.paid_amount",
                               store=True, digits_compute=dp.get_precision('Product Price'),
                               readonly=True)
    advanced_deposit = fields.Float(string='Advanced Deposit', compute="_compute_advanced_deposit",
                                    store=True, digits_compute=dp.get_precision('Product Price'),
                                    readonly=True)
    balance = fields.Float(string='Balance', compute="_compute_balance", store=True,
                           digits_compute=dp.get_precision('Product Price'), readonly=True)

    @api.depends('total_rent_price', 'advanced_deposit')
    def _compute_balance(self):
        for record in self:
            record.balance = record.total_rent_price - record.advanced_deposit

    @api.depends('previous_deposit', 'new_deposit')
    def _compute_advanced_deposit(self):
        for record in self:
            record.advanced_deposit = record.previous_deposit + record.new_deposit

    @api.depends('period_rent_price', 'extra_driver_charge', 'other_extra_charges')
    def _compute_total_rent_price(self):
        for record in self:
            record.total_rent_price = record.period_rent_price + \
                                      record.extra_driver_charge + record.other_extra_charges

    @api.depends('daily_rental_price', 'total_rental_period')
    def _compute_period_rent_price(self):
        for record in self:
            record.period_rent_price = record.total_rental_period * record.daily_rental_price

    @api.depends('new_return_date')
    def _compute_total_rental_period(self):
        for record in self:
            if record.exit_datetime and record.new_return_date:
                start = datetime.strptime(record.exit_datetime.split()[0],
                                          DEFAULT_SERVER_DATE_FORMAT)
                end = datetime.strptime(record.new_return_date,
                                        DEFAULT_SERVER_DATE_FORMAT)
                record.total_rental_period = (end - start).days

    @api.depends('total_rental_period', 'extra_driver_charge_per_day')
    def _compute_extra_driver_charge(self):
        for record in self:
            if record.total_rental_period:
                record.extra_driver_charge = record.total_rental_period * \
                                             record.extra_driver_charge_per_day

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet_rental.document_extend') or 'New'
        result = super(FleetRentalDocumentExtend, self).create(vals)
        return result

    @api.multi
    def action_confirm(self):
        for ext in self:
            ext.document_rent_id.sudo().state = 'extended'
            ext.document_rent_id.sudo().extend_return_date = ext.new_return_date
            ext.state = 'confirmed'

    @api.multi
    def print_extend(self):
        return self.env['report'].get_action(self, 'fleet_rental_document.report_extend')

    @api.multi
    def action_view_invoice(self):
        return self.mapped('document_id').action_view_invoice()
