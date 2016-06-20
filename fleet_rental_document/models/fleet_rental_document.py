# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import openerp.addons.decimal_precision as dp


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

    allowed_kilometer_per_day = fields.Integer(string='Allowed kilometer per day', related="vehicle_id.allowed_kilometer_per_day", store=False, readonly=True)
    rate_per_extra_km = fields.Float(string='Rate per extra km', related="vehicle_id.rate_per_extra_km", store=False, readonly=True)
    daily_rental_price = fields.Float(string='Daily Rental Price', related="vehicle_id.daily_rental_price", store=False, readonly=True)

    exit_datetime = fields.Datetime(string='Exit Date and Time')

    return_datetime = fields.Datetime(string='Return Date and Time')

    total_rental_period = fields.Integer(string='Total Rental Period', compute="_compute_total_rental_period", store=True, readonly=True)

    period_rent_price = fields.Float(string='Period Rent Price', compute="_compute_period_rent_price", store=True, digits_compute=dp.get_precision('Product Price'), readonly=True)

    check_line_ids = fields.One2many('fleet_rental.check_line', 'document_id', string='Vehicle rental check lines')

    @api.model
    def default_get(self, fields_list):
        result = super(FleetRentalDocument, self).default_get(fields_list)
        document_id= self._context.get('active_id', False)
        items = self.env['fleet_rental.item_to_check'].search([])
        check_line_obj = self.env['fleet_rental.check_line']

        result['check_line_ids'] = [(0, 0, {'item_id': item.id}) for item in items]

        return result

    @api.depends('exit_datetime', 'return_datetime')
    def _compute_total_rental_period(self):
        if self.exit_datetime and self.return_datetime:
            start = datetime.strptime(self.exit_datetime, DTF)
            end = datetime.strptime(self.return_datetime, DTF)
            self.total_rental_period = (end - start).days

    @api.depends('total_rental_period')
    def _compute_period_rent_price(self):
        if self.total_rental_period:
            self.period_rent_price = self.total_rental_period * self.daily_rental_price
