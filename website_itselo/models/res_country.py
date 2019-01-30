# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Country(models.Model):
    _inherit = 'res.country.state'

    district_ids = fields.One2many('res.state.district', 'state_id', string='Districts')
    city_ids = fields.One2many('res.city', 'state_id', string='City')


class StateDistrict(models.Model):
    _description = "State district"
    _name = 'res.state.district'
    _order = 'name'

    state_id = fields.Many2one('res.country.state', string='State', required=True)
    name = fields.Char(string='District Name', required=True)
    city_ids = fields.One2many('res.city', 'district_id', string='City')

    _sql_constraints = [
        ('name_code_uniq', 'unique(state_id, name)', 'The area should be unique for the region!')
    ]


class City(models.Model):
    _inherit = 'res.city'

    district_id = fields.Many2one('res.state.district', string='District')

    @api.onchange('district_id')
    def _onchange_district_id(self):
        self.state_id = self.district_id.state_id.id
