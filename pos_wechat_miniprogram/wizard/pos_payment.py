# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class PosMakePayment(models.TransientModel):
    _inherit = 'pos.make.payment'

    journal_wechat = fields.Selection(related='journal_id.wechat')
    wechat_order_id = fields.Many2one('wechat.order', string='WeChat Order to refund')
    micropay_id = fields.Many2one('wechat.micropay', string='Micropay to refund')

    @api.onchange('order_ref', 'journal_wechat')
    def update_wechat_order(self):
        super(PosMakePayment, self).update_wechat_order()
        if self.journal_wechat == 'jsapi':
            order = self.env['pos.order'].browse(self.env.context.get('active_id', False))
            record = self.env['pos.miniprogram.order'].search([('order_id', '=', order.id)]).wechat_order_id
            self.wechat_order_id = record
            self.micropay_id = False
