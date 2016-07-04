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

    partner_id = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)], required=True)

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", required=True)
    account_move_ids = fields.One2many('account.move', 'fleet_rental_document_id', string='Entries', readonly=True)
    account_move_lines_ids = fields.One2many('account.move.line', 'fleet_rental_document_id', string='Entrie lines', readonly=True)
    allowed_kilometer_per_day = fields.Integer(string='Allowed kilometer per day')
    rate_per_extra_km = fields.Float(string='Rate per extra km')
    daily_rental_price = fields.Float(string='Daily Rental Price')
    odometer_before = fields.Float(string='Odometer', readonly=True, default=0)

    extra_driver_charge_per_day = fields.Float(string='Extra Driver Charge per day', digits_compute=dp.get_precision('Product Price'), default=0)
    other_extra_charges = fields.Float(string='Other Extra Charges', digits_compute=dp.get_precision('Product Price'), default=0)

    exit_datetime = fields.Datetime(string='Exit Date and Time')
    return_datetime = fields.Datetime(string='Return Date and Time')

    total_rental_period = fields.Integer(string='Total Rental Period')
    total_rent_price = fields.Float(string='Total Rent Price', digits_compute=dp.get_precision('Product Price'))

    period_rent_price = fields.Float(string='Period Rent Price', digits_compute=dp.get_precision('Product Price'))
    extra_driver_charge = fields.Float(string='Extra Driver Charge', digits_compute=dp.get_precision('Product Price'))
    advanced_deposit = fields.Float(string='Advanced Deposit', store=True, digits_compute=dp.get_precision('Product Price'), readonly=True)
    balance = fields.Float(string='Balance', compute="_compute_balance", store=True, digits_compute=dp.get_precision('Product Price'), readonly=True)

    check_line_ids = fields.One2many('fleet_rental.check_line', 'document_id', string='Vehicle rental check lines')
    part_line_ids = fields.One2many('fleet_rental.svg_vehicle_part_line', 'document_id', string='Vehicle part')

    invoice_ids = fields.Many2many("account.invoice", string='Invoices', compute="_get_invoiced", readonly=True, copy=False)
    invoice_count = fields.Integer(string='# of Invoices', compute='_get_invoiced', readonly=True)
    invoice_line_ids = fields.One2many('account.invoice.line', 'fleet_rental_document_id', string='Invoice Lines', copy=False)

    png_file = fields.Text('PNG', compute='_compute_png', store=False)

    @api.depends('total_rent_price', 'account_move_lines_ids')
    def _compute_balance(self):
        return
        for record in self:
            account_receivable = record.partner_id.property_account_receivable_id.id
            if record.account_move_lines_ids:
                record.account_move_lines_ids[0].move_id.fleet_rental_document_id = [(4, self.id)]
            mutuals_recs = self.env['account.move.line'].search([('fleet_rental_document_id', '=', self.id), ('account_id', '=', account_receivable)])
            total_duty = 0
            total_paid = 0
            for r in mutuals_recs:
                total_duty += r.debit
                total_paid += r.credit
            record.balance = total_paid - total_duty
            record.advanced_deposit = total_paid

    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        for record in self:
            record.allowed_kilometer_per_day = record.vehicle_id.allowed_kilometer_per_day
            record.rate_per_extra_km = record.vehicle_id.rate_per_extra_km
            record.daily_rental_price = record.vehicle_id.daily_rental_price
            record.odometer_before = record.vehicle_id.odometer

    @api.onchange('daily_rental_price', 'vehicle_id', 'exit_datetime', 'return_datetime', 'return_datetime', 'extra_driver_charge_per_day', 'other_extra_charges')
    def all_calculations(self):
        for record in self:
            if record.exit_datetime and record.return_datetime:
                start = datetime.strptime(record.exit_datetime, DTF)
                end = datetime.strptime(record.return_datetime, DTF)
                record.total_rental_period = (end - start).days
            record.period_rent_price = record.total_rental_period * record.daily_rental_price
            record.total_rent_price = record.period_rent_price + record.extra_driver_charge + record.other_extra_charges
            record.extra_driver_charge = record.total_rental_period * record.extra_driver_charge_per_day

    @api.multi
    def _compute_png(self):
        for rec in self:
            f = open('/'.join([os.path.dirname(os.path.realpath(__file__)),
                               'static/src/img/car-cutout.svg']), 'r')
            svg_file = f.read()
            dom = etree.fromstring(svg_file)
            for line in rec.part_line_ids:
                if line.state == 'broken':
                    for el in dom.xpath('//*[@id="%s"]' % line.part_id.path_ID):
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
        items = self.env['fleet_rental.item_to_check'].search([])
        parts = self.env['fleet_rental.svg_vehicle_part'].search([])

        result['check_line_ids'] = [(5, 0, 0)] + [(0, 0, {'item_id': item.id,'exit_check_yes': False, 'exit_check_no': False,'exit_check_yes': False, 'exit_check_no': False,}) for item in items]
        result['part_line_ids'] = [(5, 0, 0)] + [(0, 0, {'part_id': part.id}) for part in parts]
        result['exit_datetime'] = fields.Datetime.now()
        result['return_datetime'] = fields.Datetime.to_string(datetime.utcnow() + timedelta(days=1))
        return result

