# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

# -*- coding: utf-8 -*-
from odoo import fields, models


class PosOrderReceipt(models.Model):
    _name = "pos.order_receipt"

    name = fields.Char('Name')
    qweb_template = fields.Text('Qweb')


class RestaurantPrinter(models.Model):
    _inherit = 'restaurant.printer'

    receipt_format_id = fields.Many2one('pos.order_receipt', string='Printing Template')
