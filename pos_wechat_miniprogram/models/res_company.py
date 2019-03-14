# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class Company(models.Model):
    _inherit = "res.company"

    multi_session_ids = fields.One2many('pos.multi_session', 'company_id', string='Multi-Sessions')
