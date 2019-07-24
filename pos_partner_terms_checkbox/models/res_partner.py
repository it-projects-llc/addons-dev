# Copyright 2018-2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0.html).
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    terms_and_conditions = fields.Boolean("Terms & Conditions")
