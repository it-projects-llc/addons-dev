# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, api, fields


class PosOrder(models.Model):
    _inherit = 'pos.order'

    order_from_miniprogram = fields.Boolean(default=False)
    # mp_order_ids = fields.One2many('pos.miniprogram.order', 'order_id', string="Mini-program Order")

    @api.model
    def create_from_ui(self, orders):
        res = super(PosOrder, self).create_from_ui(orders)
        for o in orders:
            data = o.get('data')
            submitted_references = data.get('name')
            order = self.search([('pos_reference', '=', submitted_references), ('order_from_miniprogram', '=', True)])
            if order:
                miniprogram_data = data.get("miniprogram_order")
                miniprogram_order = self.env['pos.miniprogram.order'].browse(miniprogram_data.get('id'))
                if miniprogram_order:
                    miniprogram_order.write({
                        'state': 'done',
                        'order_id': order.id,
                        'confirmed_from_pos': True
                    })
        return res
