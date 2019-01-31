# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    limit = fields.Float(string="Limit", translate=True)
    total = fields.Float(string="Total", readonly=True, translate=True)

    send_email_to_seller = fields.Boolean(string="Send notification to Email", translate=True, default=False)
    seller_email_template_id = fields.Many2one("mail.template", string="Email Template",
                                               domain="[('model_id.model','=','res.partner')]", translate=True)

    is_delivery = fields.Boolean('Это доставщик')
    fleet_id = fields.Many2one("fleet.vehicle", string="Автомобиль")
    district_id = fields.Many2one('res.state.district', string='District', ondelete='restrict')
    city_id = fields.Many2one('res.city', string='City', ondelete='restrict')
    house = fields.Char('House')
    flat = fields.Char('Flat')
    office = fields.Char('Office')
    inn = fields.Char(string='INN', size=12)
    kpp = fields.Char(string='KPP', size=9)
    okpo = fields.Char(string='OKPO', size=14)

    @api.onchange('send_email_to_seller')
    def _onchange_send_email_to_seller(self):
        if self.send_email_to_seller:
            self.seller_email_template_id = self.env.ref('website_itselo.partner_total_limit_email_template').id
        else:
            self.seller_email_template_id = False

    @api.onchange('city_id')
    def _onchange_state_id(self):
        self.state_id = self.city_id.state_id.id

    @api.onchange('state_id')
    def _onchange_state_id(self):
        self.country_id = self.state_id.country_id.id

    @api.onchange('district_id')
    def _onchange_state_id(self):
        self.state_id = self.district_id.state_id.id

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_('%s (copy)') % self.name)
        return super(Partner, self).copy(default)

    @api.multi
    def send_email_to_marketplace_seller(self):
        self.ensure_one()
        if self.send_email_to_seller:
            template_id = self.seller_email_template_id or False
            if not template_id:
                raise UserError(_('Please specify email template to send the notification. Model: res.partner'))
            template_id.send_mail(self.id, True)

            _logger.info("Sent an email about reaching the limit for the marketplace seller: %s" % (self.name))
