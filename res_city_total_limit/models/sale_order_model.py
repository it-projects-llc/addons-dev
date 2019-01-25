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
        return res

    @api.multi
    def action_unlock(self):
        super(SaleOrder, self).action_unlock()
        for r in self:
            r.partner_id.city_id.update_total()
