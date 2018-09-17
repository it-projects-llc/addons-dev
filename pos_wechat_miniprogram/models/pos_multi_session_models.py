# Copyright 2019 Gabbasov Dinar <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class PosMultiSession(models.Model):
    _inherit = 'pos.multi_session'

    shop_id = fields.Many2one('res.partner', string='Shop')
