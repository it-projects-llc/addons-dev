from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    extra_price = fields.Float('Extra Price')
