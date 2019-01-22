# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class City(models.Model):
    _inherit = 'res.city'

    limit = fields.Float(string="Limit")
    total = fields.Float(string="Total", readonly=True, compute='_compute_total')
    partner_ids = fields.One2many('res.partner', 'city_id', string='Partners')

    @api.depends('limit', 'partner_ids', 'partner_ids.city_id', 'partner_ids.sale_order_ids',
                 'partner_ids.sale_order_ids.partner_id', 'partner_ids.sale_order_ids.state')
    def _compute_total(self):
        for r in self:
            confirmed_orders_total = 0
            orders_ids = []
            for partner in r.partner_ids:
                orders = partner.sale_order_ids.filtered(lambda o:
                                                         o.state == 'sale' and o.amount_taken_into_account is False)
                confirmed_orders_total += sum(order.amount_total for order in orders)
                orders_ids.extend(orders.ids)
            if confirmed_orders_total >= r.limit:
                # TODO: send notification to email
                r.total = 0.0
                sale_orders = self.env["sale.order"].browse(orders_ids)
                sale_orders.write({
                    "amount_taken_into_account": True
                })
            else:
                r.total = confirmed_orders_total
