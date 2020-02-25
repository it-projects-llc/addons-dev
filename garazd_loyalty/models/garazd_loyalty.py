# -*- coding: utf-8 -*-

from odoo import fields, models


class GarazdLoyalty(models.Model):
    _name = "garazd.loyalty"
    _description = "Loyalty System Levels"

    name = fields.Char('Level Name')
    percent = fields.Integer('Discount Percent')
    amount_from = fields.Float('Purchases from')
