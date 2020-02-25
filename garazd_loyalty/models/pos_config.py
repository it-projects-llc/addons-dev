# -*- coding: utf-8 -*-

from odoo import fields, models


class PosOrder(models.Model):
    _inherit = "pos.config"

    loyalty_card_offer = fields.Boolean('Offer loyalty card', default=True)
