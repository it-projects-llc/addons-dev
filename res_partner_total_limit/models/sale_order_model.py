# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    amount_taken_into_account_user = fields.Boolean(default=False)

    def action_updated_sale_order_partner(self):
        if self.state == 'sale' and self.marketplace_seller_id and self.marketplace_seller_id.seller:
            lines = self.search([('marketplace_seller_id', '=', self.marketplace_seller_id.id),
                                 ('state', '=', 'sale'), ('amount_taken_into_account_user', '=', False)])
            confirmed_order_lines_total_price = 0
            confirmed_order_lines_total_price += sum(line.price_total for line in lines)

            if confirmed_order_lines_total_price >= self.marketplace_seller_id.limit:
                # TODO: from_to
                # TODO: send only one message
                composer = self.env['mail.compose.message'].with_context({
                    'default_composition_mode': 'comment',
                    'default_model': self._name,
                    'default_res_id': self.id,
                }).sudo().create({
                    'body': '<p> Для Вас достигнут лимит в ' + str(confirmed_order_lines_total_price) + ' рублей </p>',
                    'partner_ids': [(4, self.marketplace_seller_id.id)]
                })
                composer.send_mail()
                self.marketplace_seller_id.write({
                    "total": 0.0
                })
                lines.write({
                    "amount_taken_into_account_user": True
                })
            else:
                self.marketplace_seller_id.write({
                    "total": confirmed_order_lines_total_price
                })
