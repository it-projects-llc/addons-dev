# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_taken_into_account = fields.Boolean(default=False)

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for r in self:
            r.partner_id.city_id.update_total()
            r.order_line.action_updated_sale_order_partner()
        return res

    @api.multi
    def action_unlock(self):
        super(SaleOrder, self).action_unlock()
        for r in self:
            r.partner_id.city_id.update_total()
            r.order_line.action_updated_sale_order_partner()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    amount_taken_into_account_user = fields.Boolean(default=False)

    @api.multi
    def action_updated_sale_order_partner(self):
        for r in self:
            if r.marketplace_seller_id and r.marketplace_seller_id.seller:
                lines = self.search([('marketplace_seller_id', '=', r.marketplace_seller_id.id),
                                     ('state', '=', 'sale'), ('amount_taken_into_account_user', '=', False)])
                confirmed_order_lines_total_price = 0
                confirmed_order_lines_total_price += sum(line.price_total for line in lines)
                r.marketplace_seller_id.write({
                    "total": confirmed_order_lines_total_price
                })

                if confirmed_order_lines_total_price >= r.marketplace_seller_id.limit:
                    r.marketplace_seller_id.send_email_to_marketplace_seller()
                    r.marketplace_seller_id.write({
                        "total": 0.0
                    })
                    lines.write({
                        "amount_taken_into_account_user": True
                    })
