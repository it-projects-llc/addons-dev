# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def _discount_total_user(self):
        return self.env.ref('point_of_sale.group_pos_manager')

    discount_total_group_id = fields.Many2one(
        'res.groups', string='Total Discount Group', default=_discount_total_user,
        help='Group allows to set total discount for POS Orders.')


class pos_order(models.Model):
    _inherit = "pos.order"

    discount_total_user_id = fields.Many2one(
        'res.users', string='Total discount approval',
        help="Person who authorized set total discount for POS Orders")

    @api.model
    def _order_fields(self, ui_order):
        res = super(pos_order, self)._order_fields(ui_order)
        if ui_order.get('discount_total_user_id') is not None:
            res['discount_total_user_id'] = ui_order['discount_total_user_id']
        return res
