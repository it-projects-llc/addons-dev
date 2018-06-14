# -*- coding: utf-8 -*-
# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, checkin=False, checkout=False, attributes=None, **kwargs):
        res = super(SaleOrder, self)._cart_update(product_id, line_id, add_qty, set_qty, attributes, **kwargs)
        if checkin and checkout:
            line_id = res['line_id']
            order_line = self.env['sale.order.line'].sudo().browse(line_id)
            order_line.write({
                'checkin': checkin,
                'checkout': checkout,
            })
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    checkin = fields.Char(string='Checkin', default=False)
    checkout = fields.Char(string='Checkout', default=False)
