# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    total = fields.Float(string="Total", readonly=True, compute='_compute_total')
    limit = fields.Float(string="Limit", readonly=True, compute='_compute_total')

    @api.depends('limit', 'seller', 'sale_order_ids', 'sale_order_ids.state')
    def _compute_total(self):
        for r in self:
            confirmed_orders_total = 0
            if r.seller:
                orders = r.sale_order_ids.filtered(lambda o:
                                                   o.state == 'sale' and o.amount_taken_into_account_user is False)
                confirmed_orders_total += sum(order.amount_total for order in orders)
                if confirmed_orders_total >= r.limit:
                    # TODO: send notification to email
                    r.total = 0.0
                    orders.write({
                        "amount_taken_into_account_user": True
                    })
                else:
                    r.total = confirmed_orders_total
