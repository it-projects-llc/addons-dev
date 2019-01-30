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
from odoo import tools
import logging
_logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    @api.multi
    def hide_mp_menus_to_user(self, menu_data):
        """ Return the ids of the menu items hide to the user. """
        menu_ids = []
        core_website_menu_id = self.env.ref('website.menu_website_configuration').id
        if core_website_menu_id in menu_data:
            menu_ids.extend((
                self.env.ref('odoo_marketplace.wk_seller_website_menu').id,
            ))
        else:
            menu_ids = []

        officer_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_officer_group')[1]
        groups_ids = self.env.user.sudo().groups_id.ids
        if officer_group in groups_ids:
            try:
                menu_ids.extend((self.env.ref('odoo_marketplace.wk_seller_payment_request').id,))
            except Exception as e:
                pass
        return menu_ids

    @api.multi
    def update_mp_menus(self, res):
        if not res:
            return res
        if self.env.user.has_group('odoo_marketplace.marketplace_draft_seller_group') and not self.env.user.has_group('odoo_marketplace.marketplace_officer_group'):
            seller_menu_id = self.env['ir.model.data'].get_object_reference(
                'odoo_marketplace', 'wk_seller_dashboard_menu1_sub_menu1')[1]
            seller_shops_menu_id = self.env['ir.model.data'].get_object_reference(
                'odoo_marketplace', 'wk_seller_dashboard_menu1_sub_menu2')[1]
            for dictionary in res:
                if dictionary.get("id", False) == seller_menu_id:
                    dictionary["name"] = _("My Profile")
                if dictionary.get("id", False) == seller_shops_menu_id:
                    dictionary["name"] = _("My Shop")
        return res

    @api.multi
    def read(self, list1, load="_classic_read"):
        res = super(IrUiMenu, self).read(list1, load)
        return self.update_mp_menus(res)

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        """ Return the ids of the menu items visible to the user. """
        res = super(IrUiMenu, self)._visible_menu_ids(debug=debug)
        to_remove_menu_ids = self.hide_mp_menus_to_user(menu_data=res)
        res = res - set(to_remove_menu_ids)
        return res
