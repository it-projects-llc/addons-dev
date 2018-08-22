# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api, _
from odoo.exceptions import UserError

CHANNEL_NAME = "wechat.miniprogram"

class WeChatOrder(models.Model):
    _inherit = 'wechat.order'

    note = fields.Text(string='Note')
    table_id = fields.Many2one('restaurant.table', string='Table', help='The table where this order was served')
    customer_count = fields.Integer(string='Guests',
                                    help='The amount of customers that have been served by this order.')
    order_from_miniprogram = fields.Boolean(default=False)

    @api.model
    def create_from_miniprogram_ui(self, lines, create_vals):
        if self.env.user.number_verified is False:
            raise UserError(_("Mobile phone number not specified for User: %s (id: %s)") % (self.env.user.name, self.env.user.id))
        pay_method = create_vals.get('miniprogram_pay_method')
        create_vals['order_from_miniprogram'] = True

        if pay_method == 0:
            # create new wechat order, pay and send to POS
            return self.create_jsapi_order(lines, create_vals)
        elif pay_method == 1:
            # create new wechat order (without pay) and send to POS
            debug = self.env['ir.config_parameter'].sudo().get_param('wechat.local_sandbox') == '1'
            vals = {
                'trade_type': 'NATIVE',
                'line_ids': [(0, 0, line) for line in lines],
                'debug': debug,
            }
            if create_vals:
                vals.update(create_vals)
            order = self.sudo().create(vals)
            order._send_message_to_pos()
            return {'order_id': order.id}
        else:
            raise UserError(_('Pay Method %s is not defined'), pay_method)

    @api.multi
    def _prepare_mp_message(self):
        """
        To prepare the message of mini-program for POS
        """
        self.ensure_one()
        fields = ['id', 'note', 'table_id', 'customer_count', 'order_from_miniprogram', 'state', 'line_ids']
        return self.read(fields)[0]

    @api.multi
    def _send_message_to_pos(self):
        self.ensure_one()
        message = self._prepare_mp_message()
        for pos in self.env['pos.config'].search([('allow_message_from_miniprogram', '=', True)]):
            self.env['pos.config']._send_to_channel_by_id(self._cr.dbname, pos.id, CHANNEL_NAME, message)

    def on_notification(self, data):
        order = super(WeChatOrder, self).on_notification(data)
        if order.order_from_miniprogram:
            order._send_message_to_pos()
        return order
