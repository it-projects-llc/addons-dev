# -*- coding: utf-8 -*-

from odoo import api, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def create(self, values):
        pos_order = super(PosOrder, self).create(values)
        if pos_order.partner_id:
            pos_order.partner_id.set_loyalty_level()
        return pos_order
