# -*- coding: utf-8 -*-
# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PosOrderReceipt(models.Model):
    _name = "pos.order_receipt"

    name = fields.Char('Name')
    qweb_template = fields.Text('Qweb')


class RestaurantPrinter(models.Model):
    _inherit = 'restaurant.printer'

    receipt_format_id = fields.Many2one('pos.order_receipt', string='Printing Template')


class PosConfig(models.Model):
    _inherit = 'pos.config'

    print_transfer_info_in_kitchen = fields.Boolean(string='Print Transfer of Order in the Kitchen',
                                                    help='Print transfer info of an order in the kitchen', default=True)
