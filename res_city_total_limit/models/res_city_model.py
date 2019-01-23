# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class City(models.Model):
    _inherit = 'res.city'

    limit = fields.Float(string="Limit", translate=True)
    total = fields.Float(string="Total", readonly=True, translate=True)
    partner_ids = fields.One2many('res.partner', 'city_id', string='Partners', translate=True)
    representative_id = fields.Many2one('res.partner', string='Representative of City',
                                        help='An email will be sent to this representative when the limit is reached.',
                                        translate=True)
    expected_delivery_time = fields.Integer(string='Expected Delivery Time (days)', default=0, translate=True)

    @api.multi
    def update_total(self):
        self.ensure_one()
        confirmed_orders_total = 0
        orders_ids = []

        for partner in self.partner_ids:
            orders = partner.sale_order_ids.filtered(lambda o:
                                                     o.state == 'sale' and o.amount_taken_into_account is False)
            confirmed_orders_total += sum(order.amount_total for order in orders)
            orders_ids.extend(orders.ids)

        if confirmed_orders_total >= self.limit:
            # TODO: from_to
            # TODO: send only one message
            composer = self.env['mail.compose.message'].with_context({
                'default_composition_mode': 'comment',
                'default_model': self._name,
                'default_res_id': self.id,
            }).sudo().create({
                'body': '<p> Достигнут лимит по городу ' + str(self.name) + ' на сумму ' + str(confirmed_orders_total)
                        + ' рублей </p>',
                'partner_ids': [(4, self.representative_id.id)]
            })
            composer.send_mail()
            self.total = 0.0
            sale_orders = self.env["sale.order"].browse(orders_ids)
            sale_orders.write({
                "amount_taken_into_account": True
            })
        else:
            self.total = confirmed_orders_total
