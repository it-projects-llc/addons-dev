# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    allow_message_from_miniprogram = fields.Boolean('Allow receiving messages from the mini-program', default=True)
