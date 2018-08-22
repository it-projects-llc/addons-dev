# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WeChatOrder(models.Model):
    _inherit = 'wechat.order'

    note = fields.Text(string='Note')
    table_id = fields.Many2one('restaurant.table', string='Table', help='The table where this order was served')
    customer_count = fields.Integer(string='Guests',
                                    help='The amount of customers that have been served by this order.')
    order_from_miniprogram = fields.Boolean(default=False)

    @api.model
    def create_from_miniprogram_ui(self, lines, create_vals):
        # TODO: check access sending message (verify mobile)

        pay_method = create_vals.get('miniprogram_pay_method')
        create_vals['order_from_miniprogram'] = True
        # miniprogram_pay_method (Pay Now - 0, Pay Later - 1)
        if pay_method == 0:
            return self.create_jsapi_order(lines, create_vals)
        elif pay_method == 1:
            message = self._get_pos_format_message(lines=lines, vals=create_vals)
            self._send_message_to_pos(message)
            return True
        else:
            raise UserError(_('Pay Method %s is not defined'), pay_method)

    def _get_pos_format_message(self, lines=None, vals=None):
        if lines or vals:
            return {
                'vals': vals,
                'lines': lines
            }
        else:
            return {
                'vals': self.read()[0],
                'lines': self.line_ids.read(['product_id', 'quantity', 'price'])[0]
            }

    def on_notification(self, data):
        order = super(WeChatOrder, self).on_notification(data)
        if order.order_from_miniprogram:
            message = order._get_pos_format_message()
            self._send_message_to_pos(message)
        return order

    def _send_message_to_pos(self, message):
        channel_name = "wechat.miniprogram"
        for pos in self.env['pos.config'].search([('allow_message_from_miniprogram', '=', True)]):
            self.env['pos.config']._send_to_channel_by_id(self._cr.dbname, pos.id, channel_name, message)
