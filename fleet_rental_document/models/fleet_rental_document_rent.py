# -*- coding: utf-8 -*-
import os
import base64
from lxml import etree
from wand.image import Image
from datetime import datetime, timedelta
from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError


class FleetRentalDocumentRent(models.Model):
    _name = 'fleet_rental.document_rent'

    _inherits = {'fleet_rental.document': 'document_id'}
    document_id = fields.Many2one('fleet_rental.document',
                                  required=True, ondelete='restrict', auto_join=True)

    name = fields.Char(string='Agreement Number', required=True,
                       copy=False, readonly=True, index=True, default='New')
    partner_id = fields.Many2one('res.partner', string="Customer",
                                 domain=[('customer', '=', True)], required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('booked', 'Booked'),
        ('confirmed', 'Confirmed'),
        ('extended', 'Extended'),
        ('returned', 'Returned'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')
    type = fields.Selection([
        ('rent', 'Rent'),
        ('extend', 'Extend'),
        ('return', 'Return'),
        ], readonly=True, index=True, change_default=True)
    origin = fields.Char(string='Source Document',
                         help="Reference of the document that produced this document.",
                         readonly=True, states={'draft': [('readonly', False)]})

    membership_type_id = fields.Many2one('sale_membership.type',
                                         related='partner_id.type_id', string='Membership')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", required=True)
    vehicle_color_id = fields.Many2one('fleet.vehicle_color',
                                       related='vehicle_id.color_id', readonly=True)
    license_plate = fields.Char('License Plate', related='vehicle_id.license_plate')
    allowed_kilometer_per_day = fields.Integer(string='Allowed kilometer per day')
    rate_per_extra_km = fields.Float(string='Rate per extra km')
    daily_rental_price = fields.Float(string='Daily Rental Price')
    extra_driver_charge_per_day = fields.Float(string='Extra Driver Charge per day',
                                               digits_compute=dp.get_precision('Product Price'),
                                               default=0)
    other_extra_charges = fields.Float(string='Other Extra Charges',
                                       digits_compute=dp.get_precision('Product Price'), default=0)
    exit_datetime = fields.Datetime(string='Exit Date and Time', required=True,
                                    default=fields.Datetime.now)
    return_date = fields.Date(string='Return Date', required=True,
                                  default=fields.Datetime.to_string(datetime.utcnow() + timedelta(days=1)))
    extend_return_date = fields.Date(string='Last extend return date',
                                             help='Last extend document return Date',
                                             default=False, readonly=True)
    total_rental_period = fields.Integer(string='Total Rental Period',
                                         compute="_compute_total_rental_period",
                                         store=True, readonly=True)
    total_rent_price = fields.Float(string='Total Rent Price', compute="_compute_total_rent_price",
                                    store=True, digits_compute=dp.get_precision('Product Price'),
                                    readonly=True)
    period_rent_price = fields.Float(string='Period Rent Price',
                                     compute="_compute_period_rent_price", store=True,
                                     digits_compute=dp.get_precision('Product Price'),
                                     readonly=True)
    extra_driver_charge = fields.Float(string='Extra Driver Charge',
                                       compute="_compute_extra_driver_charge", store=True,
                                       digits_compute=dp.get_precision('Product Price'),
                                       readonly=True)
    advanced_deposit = fields.Float(string='Advanced Deposit', related="document_id.paid_amount",
                                    store=True, digits_compute=dp.get_precision('Product Price'),
                                    readonly=True)
    balance = fields.Float(string='Balance', compute="_compute_balance", store=True,
                           digits_compute=dp.get_precision('Product Price'), readonly=True)
    check_line_ids = fields.Many2many('fleet_rental.check_line',
                                      string='Vehicle rental check lines')
    part_line_ids = fields.Many2many('fleet_rental.svg_vehicle_part_line',
                                     'fleet_rental_document_rent_svg_vehicle_part_line_rel',
                                     string='Vehicle part')
    user_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    png_file = fields.Text('PNG', compute='_compute_png', store=False)
    additional_driver_ids = fields.Many2many('fleet_rental.additional_driver')
    user_branch_id = fields.Many2one('fleet_branch.branch',
                                     default=lambda self: self.env.user.branch_id.id)
    document_extend_ids = fields.One2many('fleet_rental.document_extend', 'document_rent_id')
    extends_count = fields.Integer(string='# of Extends', compute='_get_extends', readonly=True)
    diff_datetime = fields.Datetime(string='Previous rent document return date and time')
    odometer_before = fields.Float(string='Odometer',
                                   compute='_compute_odometer', store=True, readonly=True)

    @api.one
    @api.constrains('total_rental_period')
    def _check_return_date(self):
        if self.total_rental_period < 1:
            raise UserError('Return date cannot be set before or the same as Exit Date.')

    @api.one
    @api.constrains('partner_id')
    def _check_partner(self):
        if self.partner_id.blocked:
            reason = self.env['sale_membership.log'].search([('partner_id', '=', self.partner_id.id),
                                                             ('blocked', '=', True)],
                                                            order='create_date desc',
                                                            limit=1).reason
            raise UserError('The customer %s is blocked for this reason: %s.' % (self.partner_id.name, reason))

    @api.multi
    def _compute_png(self):
        for rec in self:
            f = open('/'.join([os.path.dirname(os.path.realpath(__file__)),
                               '../static/src/img/car-cutout.svg']), 'r')
            svg_file = f.read()
            dom = etree.fromstring(svg_file)
            for line in rec.part_line_ids:
                if line.state == 'broken':
                    for el in dom.xpath('//*[@id="%s"]' % line.part_id.path_ID):
                        el.attrib['fill'] = 'red'
            f.close()
            with Image(blob=etree.tostring(dom), format='svg') as img:
                rec.png_file = base64.b64encode(img.make_blob('png'))

    @api.model
    def default_get(self, fields_list):
        result = super(FleetRentalDocumentRent, self).default_get(fields_list)
        items = self.env['fleet_rental.item_to_check'].search([])
        parts = self.env['fleet_rental.svg_vehicle_part'].search([])

        result['check_line_ids'] = [(5, 0, 0)] + [(0, 0, {'item_id': item.id, 'exit_check_yes': False, 'exit_check_no': False, 'exit_check_yes': False, 'exit_check_no': False,}) for item in items]
        result['part_line_ids'] = [(5, 0, 0)] + [(0, 0, {'part_id': part.id, 'path_ID': part.path_ID}) for part in parts]
        return result

    @api.multi
    @api.depends('exit_datetime', 'return_date')
    def _compute_total_rental_period(self):
        for record in self:
            if record.exit_datetime and record.return_date:
                start = datetime.strptime(record.exit_datetime.split()[0],
                                          DEFAULT_SERVER_DATE_FORMAT)
                end = datetime.strptime(record.return_date,
                                        DEFAULT_SERVER_DATE_FORMAT)
                record.total_rental_period = (end - start).days

    @api.multi
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

    @api.depends('period_rent_price', 'extra_driver_charge', 'other_extra_charges')
    def _compute_total_rent_price(self):
        for record in self:
            record.total_rent_price = record.period_rent_price + \
                                      record.extra_driver_charge + record.other_extra_charges

    @api.depends('total_rent_price', 'advanced_deposit')
    def _compute_balance(self):
        for record in self:
            record.balance = record.total_rent_price - record.advanced_deposit

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

    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        for record in self:
            record.allowed_kilometer_per_day = record.vehicle_id.allowed_kilometer_per_day
            record.rate_per_extra_km = record.vehicle_id.rate_per_extra_km
            record.daily_rental_price = record.vehicle_id.daily_rental_price

    @api.multi
    def action_book(self):
        for rent in self:
            rent.state = 'booked'
            rent.vehicle_id.state_id = self.env.ref('fleet_rental_document.vehicle_state_booked')

    @api.multi
    def action_cancel_booking(self):
        for rent in self:
            rent.state = 'cancel'
            self.vehicle_id.state_id = self.env.ref('fleet_rental_document.vehicle_state_active')

    @api.multi
    def action_confirm(self):
        for rent in self:
            rent.state = 'confirmed'

    @api.multi
    def action_extend(self):
        document_extend_obj = self.env['fleet_rental.document_extend']
        for rent in self:
            document_extend = document_extend_obj.create({'document_rent_id': rent.id,
                                                          'extra_driver_charge_per_day': rent.extra_driver_charge_per_day,
                                                          'other_extra_charges': rent.other_extra_charges,
                                                          })
        return self.action_view_document_extend(document_extend.id)

    @api.multi
    def action_view_document_extend(self, document_extend_id):
        action = self.env.ref('fleet_rental_document.fleet_rental_document_extend_draft_act')
        form_view_id = self.env.ref('fleet_rental_document.fleet_rental_document_extend_form').id

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [(form_view_id, 'form')],
            'target': action.target,
            # 'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}},
            'context': action.context,
            'res_model': action.res_model,
        }
        result['res_id'] = document_extend_id
        return result

    @api.multi
    def action_create_return(self):
        document_return_obj = self.env['fleet_rental.document_return']
        for rent in self:
            last_extend = self.env['fleet_rental.document_extend'].search([
                ('document_rent_id', '=', rent.id),
                ('state', '=', 'confirmed')],
                order='new_return_date desc', limit=1)
            document_return = document_return_obj.create({'document_rent_id': rent.id,
                                                          'advanced_deposit': last_extend and \
                                                          last_extend.advanced_deposit or \
                                                          rent.advanced_deposit,
                                                      })
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
            # 'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}},
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

    @api.multi
    def action_view_invoice(self):
        return self.mapped('document_id').action_view_invoice()

    @api.depends('invoice_line_ids')
    def _get_invoiced(self):
        return self.mapped('document_id')._get_invoiced()
