# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

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
