# -*- coding: utf-8 -*-
from odoo import fields, models, api


CHANNEL = "pos_orders_history"


class PosConfig(models.Model):
    _inherit = 'pos.config'

    orders_history = fields.Boolean("Orders History", help="Show all orders list in POS", default=True)

    # ir.actions.server methods:
    @api.model
    def notify_orders_updates(self):
        ids = self.env.context['active_ids']
        if len(ids):
            message = {"updated_orders": ids}
            self.search([])._send_to_channel(CHANNEL, message)
