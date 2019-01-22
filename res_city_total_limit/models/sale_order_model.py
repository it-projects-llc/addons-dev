# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_taken_into_account = fields.Boolean(default=False)
