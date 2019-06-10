# -*- coding: utf-8 -*-
# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    invoice_prefix = fields.Char('Invoice Number Prefix', default='001-001')


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create_from_ui(self, orders):
        for order in orders:
            order_data = order.get('data', {})
            if order_data.get('to_invoice', False):
                order['to_invoice'] = True

        res = super(PosOrder, self).create_from_ui(orders)

        if not len(res):
            return res

        order_records = self.browse(res)
        for order in orders:
            order_data = order.get('data', {})
            if order_data.get('to_invoice', False) and order_data.get('invoice_name', False):
                order_record = order_records.filtered(lambda o: o.pos_reference == order_data.get('name'))
                self.env['account.invoice'].search([('origin', '=', order_record.name)]).write({
                    'number': order_data.get('invoice_name'),
                    'reference': order_data.get('invoice_name'),
                    # 'name': order_data.get('invoice_name'),
                })

        return res
