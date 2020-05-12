# Copyright 2019 Gabbasov Dinar <https://it-projects.info/team/GabbasovDinar>
# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _


CHANNEL = 'pos_sale_coupons'


class SaleCouponProgram(models.Model):
    _inherit = 'sale.coupon.program'

    pos_product_id = fields.Many2one('product.product', string='POS Product',
                                     domain="[('available_in_pos', '=', True), ('sale_ok', '=', True)]",
                                     help='The product used to model the discount.')
    force_sale_before_consumption = fields.Boolean(string="Force sale the coupon", default=True,
                                                   help="Force sale the coupons before consumption"
                                                        "(for POS only)")
    pos_order_count = fields.Integer(compute='_compute_pos_order_count')
    is_code_storage_program = fields.Boolean('Code Storage Program')
    parented_storage_program = fields.Many2one('sale.coupon.program', 'Program Parent')

    @api.depends('coupon_ids.pos_order_id')
    def _compute_order_count(self):
        for program in self:
            orders = program.coupon_ids.filtered(lambda c: c.pos_order_id is not False).mapped('pos_order_id')
            program.pos_order_count = len(orders) or 0

    @api.onchange('discount_type')
    def _onchange_discount_type(self):
        for program in self:
            if program.discount_type != 'fixed_amount':
                program.is_code_storage_program = False

    def action_view_pos_orders(self):
        self.ensure_one()
        orders = self.coupon_ids.filtered(lambda c: c.pos_order_id is not False).mapped('pos_order_id')
        return {
            'name': _('POS Orders'),
            'view_mode': 'tree,form',
            'res_model': 'pos.order',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', orders.ids)]
        }

    def action_updated_coupon_program(self):
        message = {'channel': CHANNEL, 'coupon_program_data': self.read()}
        self.env['pos.config'].send_to_all_poses(CHANNEL, message)

    @api.model
    def create(self, vals):
        program = super(SaleCouponProgram, self).create(vals)
        if not vals.get('discount_line_product_id', False):
            program.discount_line_product_id.write({
                'sale_ok': True,
                'available_in_pos': True
            })
        return program


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
        message = {'channel': CHANNEL, 'coupon_data': self.read(['code', 'expiration_date', 'state', 'partner_id', 'pos_order_id', 'pos_discount_line_product_id', 'sold_via_order_id', 'program_id'])}
        self.env['pos.config'].send_to_all_poses(CHANNEL, message)

    def _check_coupon_code(self, order):
        message = {}

        applicable_programs = order._get_applicable_programs()
        if not (self.state == 'reserved' and self.sold_via_order_id):
            return super(SaleCoupon, self)._check_coupon_code(order)

        # copy-pasted from super method except state check:
        if self.expiration_date and self.expiration_date < order.date_order.date():
            message = {'error': _('This coupon %s has been used or is expired.') % (self.code)}
        # Minimum requirement should not be checked if the coupon got generated by a promotion program (the requirement should have only be checked to generate the coupon)
        elif self.program_id.program_type == 'coupon_program' and not self.program_id._filter_on_mimimum_amount(order):
            message = {'error': _('A minimum of %s %s should be purchased to get the reward') % (self.program_id.rule_minimum_amount, self.program_id.currency_id.name)}
        elif not self.program_id.active:
            message = {'error': _('The coupon program for %s is in draft or closed state') % (self.code)}
        elif self.partner_id and self.partner_id != order.partner_id:
            message = {'error': _('Invalid partner.')}
        elif self.program_id in order.applied_coupon_ids.mapped('program_id'):
            message = {'error': _('A Coupon is already applied for the same reward')}
        elif self.program_id._is_global_discount_program() and order._is_global_discount_already_applied():
            message = {'error': _('Global discounts are not cumulable.')}
        elif self.program_id.reward_type == 'product' and not order._is_reward_in_order_lines(self.program_id):
            message = {'error': _('The reward products should be in the sales order lines to apply the discount.')}
        elif not self.program_id._is_valid_partner(order.partner_id):
            message = {'error': _("The customer doesn't have access to this reward.")}
        # Product requirement should not be checked if the coupon got generated by a promotion program (the requirement should have only be checked to generate the coupon)
        elif self.program_id.program_type == 'coupon_program' and not self.program_id._filter_programs_on_products(order):
            message = {'error': _("You don't have the required product quantities on your sales order. All the products should be recorded on the sales order. (Example: You need to have 3 T-shirts on your sales order if the promotion is 'Buy 2, Get 1 Free').")}
        else:
            if self.program_id not in applicable_programs and self.program_id.promo_applicability == 'on_current_order':
                message = {'error': _('At least one of the required conditions is not met to get the reward!')}
        return message

    def action_sold_via_so(self):
        self.write({
            'state': 'reserved'
        })
