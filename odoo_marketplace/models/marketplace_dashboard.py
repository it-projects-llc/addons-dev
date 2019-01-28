# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models, fields, api, _


class marketplace_dashboard(models.Model):
    _name = "marketplace.dashboard"
    _description = "Marketplace Dashboard"

    def is_user_seller(self):
        # Works with singal id
        seller_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_draft_seller_group')[1]
        manager_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_officer_group')[1]
        groups_ids = self.env.user.sudo().groups_id.ids
        if seller_group in groups_ids and manager_group in groups_ids:
            return False
        if seller_group in groups_ids and manager_group not in groups_ids:
            return True

    @api.one
    def _is_seller_or_manager(self):
        lst = []
        if self._uid:
            seller_groups = self.env['ir.model.data'].sudo().xmlid_to_object('odoo_marketplace.marketplace_seller_group')
            manager_group = self.env['ir.model.data'].sudo().xmlid_to_object('odoo_marketplace.marketplace_officer_group')
            if self._uid in seller_groups.users.ids:
                self.is_seller = True
            if self._uid in manager_group.users.ids:
                self.is_seller = False

    @api.one
    def _get_approved_count(self):
        if self.state == 'product':
            if self.is_user_seller():
                obj = self.env['product.template'].search(
                    [('marketplace_seller_id.user_ids', '=', self._uid), ('status', '=', 'approved')])
            else:
                obj = self.env['product.template'].search(
                    [('marketplace_seller_id', '!=', False), ('status', '=', 'approved')])
            self.count_product_approved = len(obj)
        if self.state == 'seller':
            obj = self.env['res.partner'].search(
                [('seller', '=', True), ('state', '=', 'approved')])
            self.count_product_approved = len(obj)
        if self.state == 'order':
            if self.is_seller:
                user_obj = self.env['res.users'].browse(self._uid)
                obj = self.env['sale.order.line'].search(
                    [('marketplace_seller_id', '=',user_obj.partner_id.id), ('state', '=', 'done')])
            else:
                obj = self.env['sale.order.line'].search(
                    [('marketplace_seller_id', '!=', False), ('state', '=', 'done')])
            self.count_product_approved = len(obj)
        if self.state == 'payment':
            obj = self.env['seller.payment'].search(
                [('seller_id', '!=', False), ('state', '=', 'posted')])
            self.count_product_approved = len(obj)

    @api.one
    def _get_pending_count(self):
        if self.state == 'product':
            if self.is_user_seller():
                obj = self.env['product.template'].search(
                    [('marketplace_seller_id.user_ids', '=', self._uid), ('status', '=', 'pending')])
            else:
                obj = self.env['product.template'].search(
                    [('marketplace_seller_id', '!=', False), ('status', '=', 'pending')])
            self.count_product_pending = len(obj)
        if self.state == 'seller':
            obj = self.env['res.partner'].search(
                [('seller', '=', True), ('state', '=', 'pending')])
            self.count_product_pending = len(obj)
        if self.state == 'order':
            user_obj = self.env['res.users'].browse(self._uid)
            if self.is_seller:
                obj = self.env['sale.order.line'].search(
                    [('marketplace_seller_id', '=',user_obj.partner_id.id), ('state', '=', 'sale')])
            else:
                obj = self.env['sale.order.line'].search(
                    [('marketplace_seller_id', '!=', False), ('state', '=', 'sale')])
            self.count_product_pending = len(obj)
        if self.state == 'payment':
            obj = self.env['seller.payment'].search(
                [('seller_id', '!=', False), ('state', '=', 'requested')])
            self.count_product_pending = len(obj)

    @api.one
    def _get_rejected_count(self):
        if self.state == 'product':
            if self.is_user_seller():
                obj = self.env['product.template'].search(
                    [('marketplace_seller_id.user_ids', '=', self._uid), ('status', '=', 'rejected')])
            else:
                obj = self.env['product.template'].search(
                    [('marketplace_seller_id', '!=', False), ('status', '=', 'rejected')])
            self.count_product_rejected = len(obj)

        if self.state == 'seller':
            obj = self.env['res.partner'].search(
                [('seller', '=', True), ('state', '=', 'denied')])
            self.count_product_rejected = len(obj)
        if self.state == 'payment':
            obj = self.env['seller.payment'].search(
                [('seller_id', '!=', False), ('state', '=', 'confirm'), ('payment_mode', '=', 'seller_payment')])
            self.count_product_rejected = len(obj)

    color = fields.Integer(string='Color Index')
    name = fields.Char(string="Name", translate=True)
    state = fields.Selection(
        [('product', 'Product'), ('seller', 'Seller'), ('order', 'Order'), ('payment', 'Payment')])
    count_product_approved = fields.Integer(compute='_get_approved_count')
    count_product_pending = fields.Integer(compute='_get_pending_count')
    count_product_rejected = fields.Integer(compute='_get_rejected_count')
    is_seller = fields.Boolean(compute="_is_seller_or_manager")
