from odoo import fields, models


CHANNEL = 'pos_sale_coupons'


class SaleCouponProgram(models.Model):
    _inherit = 'sale.coupon.program'

    pos_product_id = fields.Many2one('product.product', string='POS Product',
                                     domain="[('available_in_pos', '=', True), ('sale_ok', '=', True)]",
                                     help='The product used to model the discount.')


class SaleCoupon(models.Model):
    _inherit = 'sale.coupon'
    pos_discount_line_product_id = fields.Many2one('product.product', related='program_id.pos_product_id',
                                                   readonly=False,
                                                   help='Product used in the sales order to apply the discount.')
    pos_order_id = fields.Many2one('pos.order', 'Applied on POS order', readonly=True,
                                   help="The POS order on which the coupon is applied")
    sold_via_order_id = fields.Many2one('pos.order', string='Sold via', readonly=True,
                                        help="The POS order on which the coupon is sold")

    def action_updated_coupon(self):
        message = {'channel': CHANNEL, 'data': self.read(['code', 'expiration_date', 'state', 'partner_id', 'pos_order_id', 'pos_discount_line_product_id', 'sold_via_order_id', 'program_id'])}
        self.env['pos.config'].search([])._send_to_channel(CHANNEL, message)
