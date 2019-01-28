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
from odoo.tools.translate import _
from odoo.exceptions import UserError


import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    @api.model
    def _default_category(self):
        obj = self.env["product.category"].search([('name', '=', _('All'))])
        return obj[0] if obj else self.env["product.category"]

    @api.model
    def get_journal_id(self):
        obj = self.env["account.journal"].search([('name', '=', _('Vendor Bills'))])
        return obj[0] if obj else self.env["account.journal"]

    auto_product_approve = fields.Boolean(string="Auto Product Approve")
    internal_categ = fields.Many2one(
        "product.category", string="Internal Category")
    warehouse_location_id = fields.Many2one(
        "stock.location", string="Warehouse Location", domain="[('usage', '=', 'internal')]")
    mp_default_warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    seller_payment_limit = fields.Integer(string="Seller Payment Limit")
    next_payment_requset = fields.Integer(string="Next Payment Request")
    group_mp_product_variant = fields.Boolean(
        string="Allow sellers for several product attributes, defining variants (Example: size, color,...)",
        group='odoo_marketplace.marketplace_seller_group',
        implied_group='product.group_product_variant'
    )
    group_mp_shop_allow = fields.Boolean(
        string="Allow sellers to manage seller shop.",
        group='odoo_marketplace.marketplace_seller_group',
        implied_group='odoo_marketplace.group_marketplace_seller_shop'
    )
    group_mp_product_pricelist = fields.Boolean(
        string="Allow sellers for Advanced pricing on product using pricelist.",
        group='odoo_marketplace.marketplace_seller_group',
        implied_group='product.group_product_pricelist'
    )

    # Inventory related field
    auto_approve_qty = fields.Boolean(string="Auto Quantity Approve")

    # Seller related field
    auto_approve_seller = fields.Boolean(string="Auto Seller Approve")
    global_commission = fields.Float(string="Global Commission")

    # Mail notification related fields
    enable_notify_admin_4_new_seller = fields.Boolean(string="Enable Notification Admin For New Seller")
    enable_notify_seller_4_new_seller = fields.Boolean(
        string="Enable Notification Seller for Seller Request")
    enable_notify_admin_on_seller_approve_reject = fields.Boolean(
        string="Enable Notification Admin On Seller Approve Reject")
    enable_notify_seller_on_approve_reject = fields.Boolean(string="Enable Notification Seller On Approve Reject")
    enable_notify_admin_on_product_approve_reject = fields.Boolean(
        string="Enable Notification Admin On Product Approve Reject")
    enable_notify_seller_on_product_approve_reject = fields.Boolean(
        string="Enable Notification Seller On Product Approve Reject")
    enable_notify_seller_on_new_order = fields.Boolean(string="Enable Notification Seller On New Order")

    notify_admin_4_new_seller_m_tmpl_id = fields.Many2one(
        "mail.template", string="Mail Template to Notify Admin For New Seller", domain="[('model_id.model','=','res.partner')]")
    notify_seller_4_new_seller_m_tmpl_id = fields.Many2one(
        "mail.template", string="Mail Template to Notify Seller On Seller Request", domain="[('model_id.model','=','res.partner')]")
    notify_admin_on_seller_approve_reject_m_tmpl_id = fields.Many2one(
        "mail.template", string="Mail Template to Notify Admin on Seller Approve/Reject", domain="[('model_id.model','=','res.partner')]")
    notify_seller_on_approve_reject_m_tmpl_id = fields.Many2one(
        "mail.template", string="Mail Template to Notify Seller On Approve/Reject", domain="[('model_id.model','=','res.partner')]")
    notify_admin_on_product_approve_reject_m_tmpl_id = fields.Many2one(
        "mail.template", string="Mail Template to Notify Admin On Product Approve/Reject", domain="[('model_id.model','=','product.template')]")
    notify_seller_on_product_approve_reject_m_tmpl_id = fields.Many2one(
        "mail.template", string="Mail Template to Notify Seller On Product Approve/Reject", domain="[('model_id.model','=','product.template')]")
    notify_seller_on_new_order_m_tmpl_id = fields.Many2one(
        "mail.template", string="Mail Template to Notify Seller On New Order", domain="[('model_id.model','=','sale.order.line')]")

    # Seller shop/profile releted field
    product_count = fields.Boolean(related="website_id.mp_product_count",
        string="Show seller's product count on website.", readonly=False)
    sale_count = fields.Boolean(related="website_id.mp_sale_count", string="Show seller's sales count on website.", readonly=False)
    shipping_address = fields.Boolean(related="website_id.mp_shipping_address",
        string="Show seller's shipping address on website.", readonly=False)
    seller_since = fields.Boolean(related="website_id.mp_seller_since", string="Show seller since Date on website.", readonly=False)
    seller_t_c = fields.Boolean(related="website_id.mp_seller_t_c",
        string="Show seller's Terms & Conditions on website.", readonly=False)
    seller_contact_btn = fields.Boolean(related="website_id.mp_seller_contact_btn",
        string='Show "Contact Seller" Button on website.', readonly=False)
    seller_review = fields.Boolean(related="website_id.mp_seller_review",
        string='Show Seller Review on website.', readonly=False)
    return_policy = fields.Boolean(related="website_id.mp_return_policy",
        string="Show seller's Retrun Policy on website.", readonly=False)
    shipping_policy = fields.Boolean(related="website_id.mp_shipping_policy",
        string="Show Seller's Shipping Policy on website.", readonly=False)
    recently_product = fields.Integer(related="website_id.mp_recently_product",
        string="# of products for recently added products menu. ", readonly=False)
    # Seller Review settings field
    review_load_no = fields.Integer(related="website_id.mp_review_load_no",
        string="No. of Reviews to load", help="Set default numbers of review to show on website.", readonly=False)
    review_auto_publish = fields.Boolean(related="website_id.mp_review_auto_publish",
        string="Auto Publish", help="Publish Customer's review automatically.", readonly=False)
    show_seller_list = fields.Boolean(related="website_id.mp_show_seller_list",
        string='Show Sellers List on website.', readonly=False)
    show_seller_shop_list = fields.Boolean(related="website_id.mp_show_seller_shop_list",
        string='Show Seller Shop List on website.', readonly=False)
    show_become_a_seller = fields.Boolean(related="website_id.mp_show_become_a_seller",string="Show Become a Seller button on Account Home Page", readonly=False)
    seller_payment_journal_id = fields.Many2one("account.journal", string="Seller Payment Journal", default=get_journal_id, domain="[('type', '=', 'purchase')]")
    mp_currency_id = fields.Many2one('res.currency', "Marketplace Currency", readonly=False)

    show_visit_shop = fields.Boolean("Show visit shop link on product page")

    seller_payment_product_id = fields.Many2one("product.product", string="Seller Payment Product", domain="[('sale_ok', '=', False),('purchase_ok', '=', False),('type','=','service')]")

    term_and_condition = fields.Html(string="Marketplace Terms & Conditions", related="website_id.mp_term_and_condition", readonly=False)
    message_to_publish = fields.Text(
        string="Review feedback message", help="Message to Customer on review publish.", related="website_id.mp_message_to_publish", readonly=False)
    sell_page_label = fields.Char(
        string="Sell Link Label", related="website_id.mp_sell_page_label", readonly=False)
    sellers_list_label = fields.Char(
        string="Seller List Link Label", related="website_id.mp_sellers_list_label", readonly=False)
    seller_shop_list_label = fields.Char(
        string="Seller Shop List Link Label", related="website_id.mp_seller_shop_list_label", readonly=False)
    landing_page_banner = fields.Binary(string="Landing Page Banner", related="website_id.mp_landing_page_banner", readonly=False)
    seller_new_status_msg = fields.Text(
        string="For New Status", related="website_id.mp_seller_new_status_msg", readonly=False)
    seller_pending_status_msg = fields.Text(
        string="For Pending Status", related="website_id.mp_seller_pending_status_msg", readonly=False)
    show_sell_menu_header = fields.Boolean(related="website_id.mp_show_sell_menu_header", string="Show Sell menu in header", readonly=False)
    show_sell_menu_footer = fields.Boolean(related="website_id.mp_show_sell_menu_footer", string="Show Sell menu in footer", readonly=False)
    # seller_denied_status_msg = fields.Text(
    #     string="For Denied Status", related="website_id.mp_seller_denied_status_msg")

    @api.onchange("warehouse_location_id")
    def on_change_location_id(self):
        if not self.warehouse_location_id:
            wl_obj = self.env["stock.location"].sudo().browse(
                self.warehouse_location_id.id)
            wh_obj = self.env["stock.warehouse"]
            whs = wh_obj.search([('view_location_id', 'parent_of', wl_obj.ids)], limit=1)
            if whs:
                self.mp_default_warehouse_id = whs.id

    # @api.onchange("mp_currency_id")
    # def on_change_mp_currency_id(self):
    #     seller_payment = self.env["seller.payment"].sudo().search([])
    #     if seller_payment:
    #         raise UserError(_("You can not change marketplace currency now."))

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.default'].sudo().set('res.config.settings', 'auto_product_approve', self.auto_product_approve)
        self.env['ir.default'].sudo().set('res.config.settings', 'internal_categ', self.internal_categ.id)
        self.env['ir.default'].sudo().set('res.config.settings', 'mp_default_warehouse_id', self.mp_default_warehouse_id.id)
        self.env['ir.default'].sudo().set('res.config.settings', 'warehouse_location_id', self.warehouse_location_id.id)
        self.env['ir.default'].sudo().set('res.config.settings', 'auto_approve_qty', self.auto_approve_qty)
        self.env['ir.default'].sudo().set('res.config.settings', 'auto_approve_seller', self.auto_approve_seller)
        self.env['ir.default'].sudo().set('res.config.settings', 'global_commission', self.global_commission)
        self.env['ir.default'].sudo().set('res.config.settings', 'seller_payment_limit', self.seller_payment_limit)
        self.env['ir.default'].sudo().set('res.config.settings', 'next_payment_requset', self.next_payment_requset)
        self.env['ir.default'].sudo().set('res.config.settings', 'enable_notify_admin_4_new_seller', self.enable_notify_admin_4_new_seller)
        self.env['ir.default'].sudo().set('res.config.settings', 'enable_notify_seller_4_new_seller', self.enable_notify_seller_4_new_seller)
        self.env['ir.default'].sudo().set('res.config.settings', 'enable_notify_admin_on_seller_approve_reject', self.enable_notify_admin_on_seller_approve_reject)
        self.env['ir.default'].sudo().set('res.config.settings', 'enable_notify_seller_on_approve_reject', self.enable_notify_seller_on_approve_reject)
        self.env['ir.default'].sudo().set('res.config.settings', 'enable_notify_admin_on_product_approve_reject', self.enable_notify_admin_on_product_approve_reject)
        self.env['ir.default'].sudo().set('res.config.settings', 'enable_notify_seller_on_product_approve_reject', self.enable_notify_seller_on_product_approve_reject)
        self.env['ir.default'].sudo().set('res.config.settings', 'enable_notify_seller_on_new_order', self.enable_notify_seller_on_new_order)
        self.env['ir.default'].sudo().set('res.config.settings', 'notify_admin_4_new_seller_m_tmpl_id', self.notify_admin_4_new_seller_m_tmpl_id.id)
        self.env['ir.default'].sudo().set('res.config.settings', 'notify_seller_4_new_seller_m_tmpl_id', self.notify_seller_4_new_seller_m_tmpl_id.id)
        self.env['ir.default'].sudo().set('res.config.settings', 'notify_admin_on_seller_approve_reject_m_tmpl_id', self.notify_admin_on_seller_approve_reject_m_tmpl_id.id)
        self.env['ir.default'].sudo().set('res.config.settings', 'notify_seller_on_approve_reject_m_tmpl_id', self.notify_seller_on_approve_reject_m_tmpl_id.id)
        self.env['ir.default'].sudo().set('res.config.settings', 'notify_admin_on_product_approve_reject_m_tmpl_id', self.notify_admin_on_product_approve_reject_m_tmpl_id.id)
        self.env['ir.default'].sudo().set('res.config.settings', 'notify_seller_on_product_approve_reject_m_tmpl_id', self.notify_seller_on_product_approve_reject_m_tmpl_id.id)
        self.env['ir.default'].sudo().set('res.config.settings', 'notify_seller_on_new_order_m_tmpl_id', self.notify_seller_on_new_order_m_tmpl_id.id)
        self.env['ir.default'].sudo().set('res.config.settings', 'seller_payment_journal_id', self.seller_payment_journal_id.id)
        seller_payment = self.env["seller.payment"].sudo().search([]) #For users who are not from marketplace group
        if not seller_payment:
            self.env['ir.default'].sudo().set('res.config.settings', 'mp_currency_id', self.mp_currency_id.id)
        self.env['ir.default'].sudo().set('res.config.settings', 'show_visit_shop', self.show_visit_shop)
        self.env['ir.default'].sudo().set('res.config.settings', 'seller_payment_product_id', self.seller_payment_product_id.id)
        self.env['ir.default'].sudo().set('res.config.settings', 'group_mp_product_variant', self.group_mp_product_variant)
        self.env['ir.default'].sudo().set('res.config.settings', 'group_mp_shop_allow', self.group_mp_shop_allow)
        self.env['ir.default'].sudo().set('res.config.settings', 'group_mp_product_pricelist', self.group_mp_product_pricelist)


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        auto_product_approve = self.env['ir.default'].get('res.config.settings', 'auto_product_approve')
        internal_categ = self.env['ir.default'].get('res.config.settings', 'internal_categ') or self._default_category().id
        mp_default_warehouse_id = self.env['ir.default'].get('res.config.settings', 'mp_default_warehouse_id')
        warehouse_location_id = self.env['ir.default'].get('res.config.settings', 'warehouse_location_id') or self._default_location().id
        auto_approve_qty = self.env['ir.default'].get('res.config.settings', 'auto_approve_qty')
        auto_approve_seller = self.env['ir.default'].get('res.config.settings', 'auto_approve_seller')
        global_commission = self.env['ir.default'].get('res.config.settings', 'global_commission')
        seller_payment_limit = self.env['ir.default'].get('res.config.settings', 'seller_payment_limit')
        next_payment_requset = self.env['ir.default'].get('res.config.settings', 'next_payment_requset')
        enable_notify_admin_4_new_seller = self.env['ir.default'].get('res.config.settings', 'enable_notify_admin_4_new_seller')
        enable_notify_seller_4_new_seller = self.env['ir.default'].get('res.config.settings', 'enable_notify_seller_4_new_seller')
        enable_notify_admin_on_seller_approve_reject = self.env['ir.default'].get('res.config.settings', 'enable_notify_admin_on_seller_approve_reject')
        enable_notify_seller_on_approve_reject = self.env['ir.default'].get('res.config.settings', 'enable_notify_seller_on_approve_reject')
        enable_notify_admin_on_product_approve_reject = self.env['ir.default'].get('res.config.settings', 'enable_notify_admin_on_product_approve_reject')
        enable_notify_seller_on_product_approve_reject = self.env['ir.default'].get('res.config.settings', 'enable_notify_seller_on_product_approve_reject')
        enable_notify_seller_on_new_order = self.env['ir.default'].get('res.config.settings', 'enable_notify_seller_on_new_order')
        notify_admin_4_new_seller_m_tmpl_id = self.env['ir.default'].get('res.config.settings', 'notify_admin_4_new_seller_m_tmpl_id')
        notify_seller_4_new_seller_m_tmpl_id = self.env['ir.default'].get('res.config.settings', 'notify_seller_4_new_seller_m_tmpl_id')
        notify_admin_on_seller_approve_reject_m_tmpl_id = self.env['ir.default'].get('res.config.settings', 'notify_admin_on_seller_approve_reject_m_tmpl_id')
        notify_seller_on_approve_reject_m_tmpl_id = self.env['ir.default'].get('res.config.settings', 'notify_seller_on_approve_reject_m_tmpl_id')
        notify_admin_on_product_approve_reject_m_tmpl_id = self.env['ir.default'].get('res.config.settings', 'notify_admin_on_product_approve_reject_m_tmpl_id')
        notify_seller_on_product_approve_reject_m_tmpl_id = self.env['ir.default'].get('res.config.settings', 'notify_seller_on_product_approve_reject_m_tmpl_id')
        notify_seller_on_new_order_m_tmpl_id = self.env['ir.default'].get('res.config.settings', 'notify_seller_on_new_order_m_tmpl_id')
        seller_payment_journal_id = self.env['ir.default'].get('res.config.settings', 'seller_payment_journal_id') or self.get_journal_id().id
        mp_currency_id = self.env['ir.default'].get('res.config.settings', 'mp_currency_id') or self.env.user.company_id.currency_id.id
        show_visit_shop = self.env['ir.default'].get('res.config.settings', 'show_visit_shop')
        group_mp_product_variant = self.env['ir.default'].get('res.config.settings', 'group_mp_product_variant')
        group_mp_shop_allow = self.env['ir.default'].get('res.config.settings', 'group_mp_shop_allow')
        group_mp_product_pricelist = self.env['ir.default'].get('res.config.settings', 'group_mp_product_pricelist')
        seller_payment_product_id = self.env['ir.default'].get('res.config.settings', 'seller_payment_product_id')
        res.update(
            auto_product_approve = auto_product_approve,
            internal_categ = internal_categ,
            mp_default_warehouse_id = mp_default_warehouse_id,
            warehouse_location_id = warehouse_location_id,
            auto_approve_qty = auto_approve_qty,

            auto_approve_seller = auto_approve_seller,
            global_commission = global_commission,
            seller_payment_limit = seller_payment_limit,
            next_payment_requset = next_payment_requset,

            enable_notify_admin_4_new_seller = enable_notify_admin_4_new_seller,
            enable_notify_seller_4_new_seller = enable_notify_seller_4_new_seller,
            enable_notify_admin_on_seller_approve_reject = enable_notify_admin_on_seller_approve_reject,
            enable_notify_seller_on_approve_reject = enable_notify_seller_on_approve_reject,
            enable_notify_admin_on_product_approve_reject = enable_notify_admin_on_product_approve_reject,
            enable_notify_seller_on_product_approve_reject = enable_notify_seller_on_product_approve_reject,
            enable_notify_seller_on_new_order = enable_notify_seller_on_new_order,

            notify_admin_4_new_seller_m_tmpl_id = notify_admin_4_new_seller_m_tmpl_id,
            notify_seller_4_new_seller_m_tmpl_id = notify_seller_4_new_seller_m_tmpl_id,
            notify_admin_on_seller_approve_reject_m_tmpl_id = notify_admin_on_seller_approve_reject_m_tmpl_id,
            notify_seller_on_approve_reject_m_tmpl_id = notify_seller_on_approve_reject_m_tmpl_id,
            notify_admin_on_product_approve_reject_m_tmpl_id = notify_admin_on_product_approve_reject_m_tmpl_id,
            notify_seller_on_product_approve_reject_m_tmpl_id = notify_seller_on_product_approve_reject_m_tmpl_id,
            notify_seller_on_new_order_m_tmpl_id = notify_seller_on_new_order_m_tmpl_id,

            seller_payment_journal_id  = seller_payment_journal_id,
            mp_currency_id  = mp_currency_id,

            show_visit_shop = show_visit_shop,
            group_mp_product_variant = group_mp_product_variant,
            group_mp_shop_allow = group_mp_shop_allow,
            group_mp_product_pricelist = group_mp_product_pricelist,

            seller_payment_product_id = seller_payment_product_id,
        )
        return res

    @api.multi
    def execute(self):
        for rec in self:
            if rec.recently_product < 1 or rec.recently_product > 20:
                raise UserError(_("Recently Added Products count should be in range 1 to 20."))
            if rec.review_load_no < 1:
                raise UserError(_("Display Seller Reviews count should be more than 0."))
            if rec.global_commission < 0 or rec.global_commission >= 100:
                raise UserError(_("Global Commission should be greater than 0 and less than 100."))
            if rec.seller_payment_limit < 0 :
                raise UserError(_("Amount Limit can't be negative."))
            if rec.next_payment_requset < 0:
                raise UserError(_("Minimum Gap can't be negative."))
        return super(ResConfigSettings, self).execute()

    @api.model
    def _default_location(self):
        """ Set default location """
        user_obj = self.env.user
        if user_obj:
            company_id = user_obj.company_id.id
            location_ids = self.env["stock.location"].sudo().search(
                [("company_id", '=', company_id), ("name", "=", "Stock"), ('usage', '=', 'internal')])
            return location_ids[0] if location_ids else self.env["stock.location"]
        return self.env["stock.location"].sudo().search([('usage', '=', 'internal')])[0]
