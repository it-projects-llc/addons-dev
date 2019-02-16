# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    customer_deselection_interval = fields.Integer(string='Customer Deselection Interval', default=0)
