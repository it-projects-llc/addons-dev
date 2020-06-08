# Copyright 2020 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).
from odoo import api, fields, models, tools
from odoo.http import request

from odoo.addons.website_sale.models.website import Website as WebsiteOriginal


class Website(models.Model):
    _inherit = "website"

    location_ids = fields.Many2many(
        "stock.location",
        string="Stock Locations",
        help="Keep empty to allow all Locations",
    )

