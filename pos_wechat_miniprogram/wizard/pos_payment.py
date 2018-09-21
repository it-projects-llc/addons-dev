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
        domain = [('order_ref', '=', self.order_ref)]
        if self.journal_wechat == 'jsapi':
            record = self.env['wechat.order'].search(domain)[:1]
            self.wechat_order_id = record
            self.micropay_id = False
