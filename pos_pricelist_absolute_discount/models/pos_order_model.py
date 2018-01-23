# -*- coding: utf-8 -*-
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    @api.multi
    def _compute_taxes(self):
        res = {
            'total_excluded': 0,
            'total_included': 0,
            'taxes': [],
        }
        for line in self:
            if line.absolute_discount:
                price = line.price_unit - line.absolute_discount
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_ids.compute_all(
                price, quantity=line.qty, product=line.product_id,
                partner=line.order_id.partner_id)
            res['total_excluded'] += taxes['total_excluded']
            res['total_included'] += taxes['total_included']
            res['taxes'] += taxes['taxes']
        return res


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _amount_line_tax(self, line, fiscal_position_id):
        if line.absolute_discount:
            taxes = line.tax_ids.filtered(lambda t: t.company_id.id == line.order_id.company_id.id)
            if fiscal_position_id:
                taxes = fiscal_position_id.map_tax(taxes, line.product_id, line.order_id.partner_id)
            price = line.price_unit - line.absolute_discount
            taxes = taxes.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id,
                                      partner=line.order_id.partner_id or False)['taxes']
            return sum(tax.get('amount', 0.0) for tax in taxes)
        else:
            return super(PosOrder, self)._amount_line_tax(line, fiscal_position_id)
