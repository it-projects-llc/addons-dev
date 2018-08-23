# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, api, fields


class PosOrder(models.Model):
    _inherit = 'pos.order'

    order_from_miniprogram = fields.Boolean(default=False)

    @api.model
    def create_from_ui(self, orders):
        res = super(PosOrder, self).create_from_ui(orders)
        for o in orders:
            submitted_references = o['data']['name']
            mp_order = self.search([('pos_reference', '=', submitted_references), ('order_from_miniprogram', '=', True)])
            if mp_order and o['data']['miniprogram_state'] != 'done':
                wechat_order = self.env['wechat.order'].browse(o['data']['miniprogram_order_id'])
                wechat_order.write({
                    'state': 'done'
                })
        return res
