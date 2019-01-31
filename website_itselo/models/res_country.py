# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CountryState(models.Model):
    _inherit = 'res.country.state'

    district_ids = fields.One2many('res.state.district', 'state_id', string='Districts')
    city_ids = fields.One2many('res.city', 'state_id', string='City')


class StateDistrict(models.Model):
    _description = "State district"
    _name = 'res.state.district'
    _order = 'name'

    state_id = fields.Many2one('res.country.state', string='State', required=True)
    name = fields.Char(string='Name', required=True)
    city_ids = fields.One2many('res.city', 'district_id', string='City')

    _sql_constraints = [
        ('name_code_uniq', 'unique(state_id, name)', 'The area should be unique for the region!')
    ]


class City(models.Model):
    _inherit = 'res.city'

    @api.model
    def _default_mail_template(self):
        try:
            return self.env.ref('website_itselo.city_total_limit_email_template').id
        except ValueError:
            return False

    limit = fields.Float(string="Limit", translate=True)
    total = fields.Float(string="Total", readonly=True, translate=True)
    partner_ids = fields.One2many('res.partner', 'city_id', string='Partners', translate=True)
    representative_id = fields.Many2one('res.partner', string='Representative',
                                        help='The representative will receive the corresponding email once the '
                                             'order limit is reached.',
                                        translate=True)
    expected_delivery_time = fields.Integer(string='Expected Delivery Time (days)', default=0, translate=True)
    send_email = fields.Boolean(string="Send notification to Email", translate=True, default=False)
    city_email_template_id = fields.Many2one("mail.template", string="Email Template",
                                             domain="[('model_id.model','=','res.city')]", translate=True,
                                             default=_default_mail_template)
    district_id = fields.Many2one('res.state.district', string='District')

    @api.onchange('district_id')
    def _onchange_district_id(self):
        self.state_id = self.district_id.state_id.id

    @api.multi
    def update_total(self):
        self.ensure_one()
        confirmed_orders_total = 0
        orders_ids = []

        for partner in self.partner_ids:
            orders = partner.sale_order_ids.filtered(lambda o:
                                                     o.state == 'sale' and o.amount_taken_into_account is False)
            confirmed_orders_total += sum(order.amount_total for order in orders)
            orders_ids.extend(orders.ids)

        self.total = confirmed_orders_total

        if confirmed_orders_total >= self.limit:
            if self.send_email:
                template_id = self.city_email_template_id
                if not template_id:
                    raise UserError(_('Please specify email template to send the notification. Model: res.city'))
                template_id.send_mail(self.id, True)

                _logger.info("Sent an email about reaching the limit for the sity: %s" % (self.name))

            self.total = 0.0
            sale_orders = self.env["sale.order"].browse(orders_ids)
            sale_orders.write({
                "amount_taken_into_account": True
            })
