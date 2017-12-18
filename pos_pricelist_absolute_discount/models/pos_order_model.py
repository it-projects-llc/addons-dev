# -*- coding: utf-8 -*-
import logging
from odoo import api, models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    @api.multi
    def _compute_taxes(self):
        result = super(PosOrderLine, self)._compute_taxes()
        res = {
            'total_excluded': 0,
            'total_included': 0,
            'taxes': [],
        }
        for line in self:
            if line.absolute_discount:
                price = line.price_unit - line.absolute_discount / line.qty
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            taxes = line.tax_ids.compute_all(
                price, quantity=line.qty, product=line.product_id,
                partner=line.order_id.partner_id)
            res['total_excluded'] += taxes['total_excluded']
            res['total_included'] += taxes['total_included']
            res['taxes'] += taxes['taxes']

        result['total_excluded'] = res['total_excluded']
        result['total_included'] = res['total_included']
        result['taxes'] = res['taxes']
        return result


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _amount_line_tax(self, line, context=None):
        result = super(PosOrder, self)._amount_line_tax(line, context)

        if line.absolute_discount:
            price = line.price_unit - line.absolute_discount / line.qty
        else:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

        taxes = line.tax_ids.compute_all(
            price, quantity=line.qty, product=line.product_id,
            partner=line.order_id.partner_id)['taxes']
        val = 0.0
        for c in taxes:
            val += c.get('amount', 0.0)

        result = val
        return result
