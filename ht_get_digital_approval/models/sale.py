# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    signature_image = fields.Binary(string='Signature')
    signature_added = fields.Boolean("Signature added?", default=False)

    @api.multi
    def action_confirm(self):
        if self.signature_added == True:
            for order in self:
                order.state = 'sale'
                order.confirmation_date = fields.Datetime.now()
                if self.env.context.get('send_email'):
                    self.force_quotation_send()
                order.order_line._action_procurement_create()
            if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
                self.action_done()
            return True
        else:
            raise UserError("Please, Get a signature from manager.")

