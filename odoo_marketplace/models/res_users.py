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

from odoo import api, fields, models, _
from odoo.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def signup(self, values, token=None):
        """ """
        context = dict(self._context)   
        if values.get('is_seller', False):
            context["is_seller"] = values.get('is_seller', False)
            values.pop("is_seller")
        return super(ResUsers, self.with_context(context)).signup(values, token)

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        user_obj = super(ResUsers, self).copy(default=default)
        if self._context.get('is_seller', False):
            # Set Default fields for seller (i.e: payment_methods, commission, location_id, etc...)
            wk_valse = {
                "payment_method": [(6, 0, user_obj.partner_id._set_payment_method())],
                "commission": self.env['ir.default'].get('res.config.settings', 'global_commission'),
                "location_id": self.env['ir.default'].get('res.config.settings', 'warehouse_location_id') or False,
                "warehouse_id": self.env['ir.default'].get('res.config.settings', 'mp_default_warehouse_id') or False,
                "auto_product_approve": self.env['ir.default'].get('res.config.settings', 'auto_product_approve'),
                "seller_payment_limit": self.env['ir.default'].get('res.config.settings', 'seller_payment_limit'),
                "next_payment_request": self.env['ir.default'].get('res.config.settings', 'next_payment_requset'),
                "auto_approve_qty": self.env['ir.default'].get('res.config.settings', 'auto_approve_qty'),
                "show_seller_since": self.env['ir.default'].get('res.config.settings', 'seller_since'),
                "show_seller_address": self.env['ir.default'].get('res.config.settings', 'shipping_address'),
                "show_product_count": self.env['ir.default'].get('res.config.settings', 'product_count'),
                "show_sale_count": self.env['ir.default'].get('res.config.settings', 'sale_count'),
                "show_return_policy": self.env['ir.default'].get('res.config.settings', 'return_policy'),
                "show_shipping_policy": self.env['ir.default'].get('res.config.settings', 'shipping_policy'),
                "show_seller_review": self.env['ir.default'].get('res.config.settings', 'seller_review'),
                "seller" : True,
            }
            user_obj.partner_id.write(wk_valse)
            # Add user to Pending seller group
            # user_obj.partner_id.seller = True
            draft_seller_group_id = self.env['ir.model.data'].get_object_reference('odoo_marketplace', 'marketplace_draft_seller_group')[1]
            groups_obj = self.env["res.groups"].browse(draft_seller_group_id)
            if groups_obj:
                for group_obj in groups_obj:
                    group_obj.write({"users": [(4, user_obj.id, 0)]})
        return user_obj

    @api.multi
    def notification_on_partner_as_a_seller(self):
        # Here Ids must be single user is
        for user_obj in self:
            if user_obj.partner_id.seller:
                template = self.env['mail.template']
                config_setting_obj = self.env['res.config.settings'].get_values()
                if config_setting_obj["enable_notify_admin_4_new_seller"] and config_setting_obj.get("notify_admin_4_new_seller_m_tmpl_id",False) and config_setting_obj["notify_admin_4_new_seller_m_tmpl_id"]:
                    # Notify to admin by admin on new seller creation
                    temp_id = config_setting_obj["notify_admin_4_new_seller_m_tmpl_id"]
                    if temp_id:
                        template.browse(temp_id).send_mail(user_obj.partner_id.id, True)
                if config_setting_obj["enable_notify_seller_4_new_seller"] and config_setting_obj.get("notify_seller_4_new_seller_m_tmpl_id",False) and config_setting_obj["notify_seller_4_new_seller_m_tmpl_id"]:
                    # Notify to Seller by admin on new seller creation
                    temp_id2 = config_setting_obj["notify_seller_4_new_seller_m_tmpl_id"]
                    if temp_id2:
                        template.browse(temp_id2).send_mail(user_obj.partner_id.id, True)
