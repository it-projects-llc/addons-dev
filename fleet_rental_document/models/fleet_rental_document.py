# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import openerp.addons.decimal_precision as dp
import base64
from lxml import etree
import os
from wand.image import Image


class FleetRentalDocument(models.Model):
    _name = 'fleet_rental.document'

    name = fields.Char(string='Agreement Number', required=True, copy=False, readonly=True, index=True, default='New')

    type = fields.Selection([
            ('rent','Rent'),
            ('extended_rent','Extended Rent'),
            ('return','Return'),
        ], readonly=True, index=True, change_default=True)

    origin = fields.Char(string='Source Document',
        help="Reference of the document that produced this document.",
        readonly=True, states={'draft': [('readonly', False)]})

    partner_id = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)])

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")

    allowed_kilometer_per_day = fields.Integer(string='Allowed kilometer per day', related="vehicle_id.allowed_kilometer_per_day", store=True, readonly=True)
    rate_per_extra_km = fields.Float(string='Rate per extra km', related="vehicle_id.rate_per_extra_km", store=True, readonly=True)
    daily_rental_price = fields.Float(string='Daily Rental Price', related="vehicle_id.daily_rental_price", store=True, readonly=True)
    odometer = fields.Float(string='Odometer', related="vehicle_id.odometer", store=True, readonly=True)

    extra_driver_charge_per_day = fields.Float(string='Extra Driver Charge per day', digits_compute=dp.get_precision('Product Price'), default=0)
    other_extra_charges = fields.Float(string='Other Extra Charges', digits_compute=dp.get_precision('Product Price'), default=0)

    exit_datetime = fields.Datetime(string='Exit Date and Time')

    return_datetime = fields.Datetime(string='Return Date and Time')

    total_rental_period = fields.Integer(string='Total Rental Period', compute="_compute_total_rental_period", store=True, readonly=True)

    period_rent_price = fields.Float(string='Period Rent Price', compute="_compute_period_rent_price", store=True, digits_compute=dp.get_precision('Product Price'), readonly=True)
    extra_driver_charge = fields.Float(string='Extra Driver Charge', compute="_compute_extra_driver_charge", store=True, digits_compute=dp.get_precision('Product Price'), readonly=True)
    total_rent_price = fields.Float(string='Total Rent Price', compute="_compute_total_rent_price", store=True, digits_compute=dp.get_precision('Product Price'), readonly=True)
    advanced_deposit = fields.Float(string='Advanced Deposit', compute="_compute_advanced_deposit", store=True, digits_compute=dp.get_precision('Product Price'), readonly=True)
    balance = fields.Float(string='Balance', compute="_compute_balance", store=True, digits_compute=dp.get_precision('Product Price'), readonly=True)

    check_line_ids = fields.One2many('fleet_rental.check_line', 'document_id', string='Vehicle rental check lines')

    invoice_ids = fields.Many2many("account.invoice", string='Invoices', compute="_get_invoiced", readonly=True, copy=False)

    invoice_count = fields.Integer(string='# of Invoices', compute='_get_invoiced', readonly=True)

    invoice_line_ids = fields.One2many('account.invoice.line', 'fleet_rental_document_id', string='Invoice Lines', copy=False)

    part_ids = fields.One2many(related='vehicle_id.part_ids')
    png_file = fields.Text('PNG', compute='_compute_png', store=False)

    @api.onchange('vehicle_id')
    def on_change_vehicle_id(self):
        self._compute_png()

    @api.multi
    def _compute_png(self):
        for rec in self:
            f = open('/'.join([os.path.dirname(os.path.realpath(__file__+ '//..//..')),  # TODO needs better decision
                               'fleet_vehicle_svg/static/src/img/car-cutout.svg']), 'r')
            svg_file = f.read()
            dom = etree.fromstring(svg_file)
            for part in rec.part_ids:
                if part.state == 'broken':
                    for el in dom.xpath('//*[@id="%s"]' % part.part_id):
                        el.attrib['fill'] = 'red'
            f.close()
            with Image(blob=etree.tostring(dom), format='svg') as img:
                rec.png_file = base64.b64encode(img.make_blob('png'))

    @api.multi
    def action_view_invoice(self):
        invoice_ids = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1')
        list_view_id = self.env.ref('account.invoice_tree').id
        form_view_id = self.env.ref('account.invoice_form').id

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'graph'], [False, 'kanban'], [False, 'calendar'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % invoice_ids.ids
        elif len(invoice_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = invoice_ids.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

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

    @api.model
    def default_get(self, fields_list):
        result = super(FleetRentalDocument, self).default_get(fields_list)
        document_id= self._context.get('active_id', False)
        items = self.env['fleet_rental.item_to_check'].search([])
        check_line_obj = self.env['fleet_rental.check_line']

        result['check_line_ids'] = [(5, 0, 0)] + [(0, 0, {'item_id': item.id,'exit_check_yes': False, 'exit_check_no': False,'exit_check_yes': False, 'exit_check_no': False,}) for item in items]

        return result

    @api.depends('exit_datetime', 'return_datetime')
    def _compute_total_rental_period(self):
        for record in self:
            if record.exit_datetime and record.return_datetime:
                start = datetime.strptime(record.exit_datetime, DTF)
                end = datetime.strptime(record.return_datetime, DTF)
                record.total_rental_period = (end - start).days

    @api.depends('total_rental_period')
    def _compute_period_rent_price(self):
        for record in self:
            if record.total_rental_period:
                record.period_rent_price = record.total_rental_period * record.daily_rental_price

    @api.depends('total_rental_period', 'extra_driver_charge_per_day')
    def _compute_extra_driver_charge(self):
        for record in self:
            if record.total_rental_period:
                record.extra_driver_charge = record.total_rental_period * record.extra_driver_charge_per_day

    @api.depends('period_rent_price', 'extra_driver_charge', 'other_extra_charges')
    def _compute_total_rent_price(self):
        for record in self:
            record.total_rent_price = record.period_rent_price + record.extra_driver_charge + record.other_extra_charges

    @api.depends('invoice_line_ids.invoice_id.state')
    def _compute_advanced_deposit(self):
        for record in self:
            advanced_deposit = 0
            for invoice_line in record.invoice_line_ids.filtered(lambda r: r.invoice_id.type == 'out_invoice'\
                                                            and r.invoice_id.state == 'paid'\
                                                            and r.product_id.name == 'Down payment'):
                advanced_deposit+= invoice_line.price_unit

            record.advanced_deposit = advanced_deposit

    @api.depends('total_rent_price', 'advanced_deposit')
    def _compute_balance(self):
        for record in self:
            record.balance = record.total_rent_price - record.advanced_deposit


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    fleet_rental_document_id = fields.Many2one('fleet_rental.document', readonly=True, copy=False)

