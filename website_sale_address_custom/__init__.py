# coding: utf-8
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from . import models
from . import controllers


def country_updates(cr, registry):
    from odoo import api
    from odoo import SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    country_records = env['res.country'].search([('address_format', '=', '%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s')])
    for rec in country_records:
        rec.write({
            'address_format': '%(street)s\n%(street2)s\n%(zip)s %(city)s %(state_code)s\n%(country_name)s'
        })
