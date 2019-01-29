# -*- coding: utf-8 -*-
# Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api
from .. import pagadito


class AcquirerPagadito(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('pagadito', 'Pagadito')])
    pagadito_uid = fields.Char('UID', help='El identificador del Pagadito Comercio', required_if_provider='pagadito')
    pagadito_wsk = fields.Char('WSK', help='La clave de acceso', required_if_provider='pagadito')

    @api.multi
    def pagadito_form_generate_values(self, values):
        sandbox = self.environment != 'prod'
        # connect
        res = pagadito.call(pagadito.OP_CONNECT, {
            'uid': self.pagadito_uid,
            'wsk': self.pagadito_wsk,
        }, sandbox=sandbox)
        token = res['value']
        # exec_trans
        order = self._txref2order(values['reference'])
        details = self._order2pagadito_details(order)
        res = pagadito.call(pagadito.OP_EXEC_TRANS, {
            'token': token,
            'ern': order.name,
            'amount': order.amount_total,
            'details': details,
        }, sandbox=sandbox)

        values['pagadito_url'] = res['value']
        return values

    @api.multi
    def _txref2order(self, reference):
        tx = self.env['payment.transaction'].search([
            ('reference', '=', reference)
        ])
        order = self.env['sale.order'].search([
            ('payment_tx_id', '=', tx.id),
        ])
        return order

    @api.model
    def _order2pagadito_details(self, order):
        res = []
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        for line in order.order_line:
            res.append({
                'quantity': line.product_uom_qty,
                'description': line.name,
                'price': line.price_unit,
                'url_product': "%s/shop/product/%s" % (base_url, line.product_id.product_tmpl_id)
            })
