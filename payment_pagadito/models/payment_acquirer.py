# -*- coding: utf-8 -*-
# Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import json
from odoo import models, fields, api
from .. import pagadito
from odoo.http import request


class AcquirerPagadito(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('pagadito', 'Pagadito')])
    pagadito_uid = fields.Char('UID', help='El identificador del Pagadito Comercio', required_if_provider='pagadito')
    pagadito_wsk = fields.Char('WSK', help='La clave de acceso', required_if_provider='pagadito')

    @api.multi
    def pagadito_form_generate_values(self, values):
        reference = values['reference']
        if reference == '/':
            # we are on /shop/payment
            # -- selecting payment method screen only
            return values
        sandbox = self.environment != 'prod'
        # connect
        res = pagadito.call(pagadito.OP_CONNECT, {
            'uid': self.pagadito_uid,
            'wsk': self.pagadito_wsk,
        }, sandbox=sandbox)
        token = res['value']
        # exec_trans
        order = request.website.sale_get_order()
        details = self._order2pagadito_details(order)
        res = pagadito.call(pagadito.OP_EXEC_TRANS, {
            'token': token,
            'ern': order.name,
            'amount': order.amount_total,
            'details': json.dumps(details),
            'currency': self._currency2pagadito_code(order.currency_id),
            'custom_params': '',  # TODO
            'allow_pending_payments': '', # What is that?
            'extended_expiration': False, # What is that?
        }, sandbox=sandbox)
        # TODO: Check for errors in response here

        values['pagadito_url'] = res['value']
        return values

    @api.model
    def _currency2pagadito_code(self, currency):
        code = currency.name
        assert code in pagadito.SUPPORTED_CURRENCY
        return code

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
        return res
