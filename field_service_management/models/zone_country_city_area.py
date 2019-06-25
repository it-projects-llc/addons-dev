# See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ZoneZone(models.Model):
    _name = 'zone.zone'

    name = fields.Char(
        string='Zone Name',
        required="1",
        help='Name of the Zone')


class CountryStateInherited(models.Model):
    _inherit = 'res.country.state'

    zone_id = fields.Many2one(
        comodel_name='zone.zone',
        string="Zone",
        help='The zone where the state is located.')


class CityCity(models.Model):
    _name = 'city.city'

    name = fields.Char(
        string='City Name',
        help='The name of the city.')
    state_id = fields.Many2one(
        comodel_name='res.country.state',
        string='State',
        help='The state where the city is located.')
    is_service = fields.Boolean(
        string='Serviceable',
        default=True,
        help='If the fields is default true.')


class AreaArea(models.Model):
    _name = 'area.area'

    name = fields.Char(
        string='Area Name',
        help='Name of the area.')
    city_id = fields.Many2one(
        comodel_name='city.city',
        string='City',
        help='The city where the area is located.')
    is_serviceable = fields.Boolean(
        string='Serviceable',
        default=True,
        help='If the fields is default true.')
