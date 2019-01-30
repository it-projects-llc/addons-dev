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
from datetime import datetime, timedelta
from lxml import etree
from odoo.osv.orm import setup_modifiers
import decimal,re
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError
import logging
_logger = logging.getLogger(__name__)

manager_fields = []

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Default methods

    @api.model
    def _set_payment_method(self):
        return_list = []
        try:
            payment_method_cheque_id = self.env['ir.model.data'].get_object_reference(
                'odoo_marketplace', 'marketplace_seller_payment_method_data2')
            if payment_method_cheque_id:
                return_list.append(payment_method_cheque_id[1])
        except Exception as e:
            pass
        try:
            payment_method_bank_transfer_id = self.env['ir.model.data'].get_object_reference(
                'odoo_marketplace', 'marketplace_seller_payment_method_data5')
            if payment_method_cheque_id:
                return_list.append(payment_method_bank_transfer_id[1])
        except Exception as e:
            pass
        return return_list if return_list else self.env['seller.payment.method']

    def _default_website_sequence(self):
        self._cr.execute("SELECT MIN(website_sequence) FROM %s" % self._table)
        min_sequence = self._cr.fetchone()[0]
        return min_sequence and min_sequence - 1 or 10

    # Fields declaration

    seller = fields.Boolean(string="Is a Seller", help="Check this box if the contact is marketplace seller.", copy=False, track_visibility='onchange')
    payment_method = fields.Many2many("seller.payment.method", string="Payment Methods",
                                      help="It's you're accepted payment method, which will be used by admin during sending the payment.", default=_set_payment_method)
    state = fields.Selection([('new', 'New'), ('pending', 'Pending for Approval'), ('approved', 'Approved'), (
        'denied', 'Denied')], string="Seller Status", default="new", copy=False, translate=True, track_visibility='onchange')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=lambda self: [
                                     ('res_model', '=', self._name)], auto_join=True, string='Attachments')
    displayed_image_id = fields.Many2one(
        'ir.attachment', domain="[('res_model', '=', 'project.task'), ('res_id', '=', id), ('mimetype', 'ilike', 'image')]", string='Displayed Image')
    # Marketplace Seller Wise setting
    set_seller_wise_settings = fields.Boolean(
        string="Override default seller perameters", copy=False)
    commission = fields.Float(string="Default Sale Commission", default=lambda self: self.env['ir.default'].get(
        'res.config.settings', 'global_commission'), read=['odoo_marketplace.marketplace_draft_seller_group'], write=['odoo_marketplace.marketplace_manager_group'], copy=False, track_visibility='onchange')
    warehouse_id = fields.Many2one(
        "stock.warehouse", string="Default Warehouse", copy=False)
    location_id = fields.Many2one("stock.location", string="Default Location", domain="[('usage', '=', 'internal')]", default=lambda self: self.env[
                                  'ir.default'].get('res.config.settings', 'warehouse_location_id') or self.env["stock.location"], copy=False)
    auto_product_approve = fields.Boolean(string="Auto Product Approve", default=lambda self: self.env[
                                          'ir.default'].get('res.config.settings', 'auto_product_approve'), copy=False)
    seller_payment_limit = fields.Integer(string="Seller Payment Limit", default=lambda self: self.env['ir.default'].get(
        'res.config.settings', 'seller_payment_limit'), read=['odoo_marketplace.marketplace_draft_seller_group'], write=['odoo_marketplace.marketplace_manager_group'], copy=False, track_visibility='onchange')
    next_payment_request = fields.Integer(string="Next Payment Request", default=lambda self: self.env['ir.default'].get(
        'res.config.settings', 'next_payment_requset'), read=['odoo_marketplace.marketplace_draft_seller_group'], write=['odoo_marketplace.marketplace_manager_group'], copy=False, track_visibility='onchange')
    auto_approve_qty = fields.Boolean(string="Auto Quantity Approve", default=lambda self: self.env[
                                      'ir.default'].get('res.config.settings', 'auto_approve_qty'), copy=False)
    total_mp_payment = fields.Monetary(
        string="Total Amount", compute="_calculate_mp_related_payment", currency_field='seller_currency_id')
    paid_mp_payment = fields.Monetary(string="Paid Amount", compute="_calculate_mp_related_payment", currency_field='seller_currency_id')
    balance_mp_payment = fields.Monetary(string="Balance Amount", compute="_calculate_mp_related_payment", currency_field='seller_currency_id')
    available_amount = fields.Monetary(string="Avalibale Amount", compute="_calculate_mp_related_payment", currency_field='seller_currency_id')
    cashable_amount = fields.Monetary(string="Cashable Amount", compute="_calculate_mp_related_payment", currency_field='seller_currency_id')
    seller_currency_id = fields.Many2one('res.currency', compute='_get_seller_currency', string="Marketplace Currency", readonly=True)
    return_policy = fields.Html(string="Return Policy", Default="Seller return policy is not defined.", copy=False, translate=True)
    shipping_policy = fields.Html(string="Shipping policy", Default="Seller shipping policy is not defined.", copy=False, translate=True)
    profile_msg = fields.Html(string="Profile Message", copy=False, translate=True)
    profile_image = fields.Binary(string="Profile Image", copy=False)
    profile_banner = fields.Binary(string="Profile Banner", copy=False)
    # Fields related to seller review
    seller_review_ids = fields.One2many(
        'seller.review', 'marketplace_seller_id', string='Review')
    average_rating = fields.Float(
        compute='_set_avg_rating', string="Average Rating")

    sol_count = fields.Float(
        compute='_compute_sol_count', string="Sales Count")

    # Shop related field
    seller_shop_id = fields.Many2one("seller.shop", string="Seller Shop", copy=False)

    #Seller List Fields
    website_published = fields.Boolean(string="Visible in Website")
    website_size_x = fields.Integer('Size X', default=1)
    website_size_y = fields.Integer('Size Y', default=1)
    website_style_ids = fields.Many2many('seller.shop.style', string='Styles')
    website_style_ids = fields.Many2many('seller.shop.style', string='Styles')
    website_sequence = fields.Integer('Website Sequence', help="Determine the display order in the Website E-commerce",
                                      default=lambda self: self._default_website_sequence())
    allow_product_variants = fields.Boolean(compute="_get_product_variant_group_info", string="Allow Product Variants", help="Allow for several product attributes, defining variants (Example: size, color,...)")
    social_media_link_ids = fields.One2many("seller.social.media.link", "seller_id", "Social Media")
    url = fields.Char(string="URL", compute="_get_page_url")
    url_handler = fields.Char("Url Handler", help="Seller URL handler", copy=False)

    #Seller status message field
    status_msg = fields.Text(string="Account Status Message", compute="_get_seller_status_msg", translate=True)

    # SQL Constraints
    _sql_constraints = [
        ('seller_shop_id_uniq', 'unique(seller_shop_id)',
        _('This shop is already assign to another seller.'))
    ]

    manager_fields.extend(['commission','seller_payment_limit','next_payment_request','auto_product_approve',
        'auto_approve_qty','location_id','warehouse_id','allow_product_variants',
        'total_mp_payment','paid_mp_payment','balance_mp_payment', 'state'])

    # compute and search field methods, in the same order of fields declaration

    @api.multi
    def _get_seller_status_msg(self):
        for obj in self:
            website_id = obj.website_id or self.env["website"].search([],limit=1)
            if obj.state == "pending":
                if website_id and website_id.mp_seller_pending_status_msg:
                    obj.status_msg = website_id.mp_seller_pending_status_msg
                else:
                    obj.status_msg = "Thank you for seller request, your request has been already sent for approval we'll process your request as soon as possible."
            elif website_id and website_id.mp_seller_new_status_msg:
                obj.status_msg = website_id.mp_seller_new_status_msg
            else:
                obj.status_msg = "Thank you for registering with us, to enjoy the benefits of our marketplace fill all your details and request for approval."

    @api.multi
    def _get_seller_currency(self):
        for obj in self:
            obj.seller_currency_id = self.env['ir.default'].get('res.config.settings', 'mp_currency_id') or self.env.user.company_id.currency_id

    @api.multi
    def _calculate_mp_related_payment(self):
        total_mp_payment = paid_mp_payment = cashable_amount = 0
        for obj in filter(lambda e: e.seller, self):
            seller_payment_objs = self.env["seller.payment"].search([("seller_id", "=", obj.id), ("state", "not in",["draft", "requested"])])
            for seller_payment in seller_payment_objs:
                #Calculate total marketplace payment for seller
                if seller_payment.state == 'confirm' and seller_payment.payment_mode == "order_paid":
                    total_mp_payment += abs(seller_payment.payable_amount)

                #Calculate total paid marketplace payment for seller
                if seller_payment.state == 'posted' and seller_payment.payment_mode == "seller_payment":
                    paid_mp_payment += abs(seller_payment.payable_amount)

                #Calculate marketplace cashable payment for seller
                if seller_payment.state == 'confirm' and seller_payment.payment_mode == "order_paid" and seller_payment.is_cashable:
                    cashable_amount += abs(seller_payment.payable_amount)

            obj.total_mp_payment = total_mp_payment
            obj.paid_mp_payment = paid_mp_payment
            obj.cashable_amount = (round(decimal.Decimal(cashable_amount - obj.paid_mp_payment), 2))

            #Calculate total balanec marketplace payment for seller
            obj.balance_mp_payment = abs(obj.total_mp_payment) - abs(obj.paid_mp_payment)

            #Calculate marketplace available payment for seller
            obj.available_amount = (round(decimal.Decimal(obj.balance_mp_payment), 2))

    @api.multi
    def _compute_sol_count(self):
        """ """
        for obj in self:
            obj.sol_count = len(self.env["sale.order.line"].search([("marketplace_seller_id", "=", obj.id)]))

    @api.multi
    def _get_product_variant_group_info(self):
        for obj in self:
            product_variant_group = self.env.ref('product.group_product_variant')
            user_obj = self.env["res.users"].sudo().search([('partner_id', '=', obj.id)])
            user_groups = user_obj.read(['groups_id'])
            if user_groups and user_groups[0].get("groups_id"):
                user_groups_ids = user_groups[0].get("groups_id")
                if product_variant_group.id in user_groups_ids:
                    obj.allow_product_variants = True
            else:
                obj.allow_product_variants = False

    @api.multi
    def _get_page_url(self):
        for obj in self:
            if obj.seller:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                base_url = base_url + "/seller/profile/"
                url_handler = str(obj.id) if not obj.url_handler else obj.url_handler
                obj.url = base_url + url_handler

    # Constraints and onchanges

    @api.onchange('state_id')
    def on_change_state_id(self):
        if self.state_id and self.state_id.country_id:
            self.country_id = self.state_id.country_id.id
        else:
            self.country_id = False

    @api.onchange('country_id')
    def on_change_country_id(self):
        if self.country_id and self.state_id and self.state_id.country_id.id != self.country_id.id:
            self.state_id = False
            return {'domain': {'state_id': [('country_id', '=', self.country_id.id)]}}
        if self.country_id:
            return {'domain': {'state_id': [('country_id', '=', self.country_id.id)]}}
        else:
            self.state_id = False
            return {'domain': {'state_id': []}}

    @api.onchange('commission', 'seller_payment_limit', 'next_payment_request')
    def on_change_payment_assest(self):
        if self.commission < 0 or self.commission >= 100:
            raise Warning(_("Commission should be greater than 0 and less than 100."))
        if self.seller_payment_limit < 0 :
            raise Warning(_("Amount Limit can't be negative."))
        if self.next_payment_request < 0:
            raise Warning(_("Minimum Gap can't be negative."))

    @api.onchange("location_id")
    def on_change_location_id(self):
        wl_obj = self.env["stock.location"].browse(self.location_id.id)
        wh_obj = self.env["stock.warehouse"]
        whs = wh_obj.search([('view_location_id.parent_left', '<=', wl_obj.parent_left),
                             ('view_location_id.parent_right', '>=', wl_obj.parent_left)], limit=1)
        if whs:
            self.warehouse_id = whs.id
        else:
            self.warehouse_id = None

    @api.onchange("set_seller_wise_settings")
    def on_change_seller_wise_settings(self):
        if not self.set_seller_wise_settings:
            vals = {}
            vals["commission"] = self.env['ir.default'].get(
                'res.config.settings', 'global_commission')
            vals["location_id"] = self.env['ir.default'].get(
                'res.config.settings', 'warehouse_location_id')
            vals["auto_product_approve"] = self.env['ir.default'].get(
                'res.config.settings', 'auto_product_approve')
            vals["seller_payment_limit"] = self.env['ir.default'].get(
                'res.config.settings', 'seller_payment_limit')
            vals["next_payment_request"] = self.env['ir.default'].get(
                'res.config.settings', 'next_payment_requset')
            vals["auto_approve_qty"] = self.env['ir.default'].get(
                'res.config.settings', 'auto_approve_qty')
            self.update(vals)

    @api.onchange("seller")
    def on_change_seller(self):
        return_list = []
        if self.seller:
            try:
                payment_method_cheque_id = self.env['ir.model.data'].get_object_reference(
                    'odoo_marketplace', 'marketplace_seller_payment_method_data2')
                if payment_method_cheque_id:
                    return_list.append(payment_method_cheque_id[1])
            except Exception as e:
                pass
            try:
                payment_method_bank_transfer_id = self.env['ir.model.data'].get_object_reference(
                    'odoo_marketplace', 'marketplace_seller_payment_method_data5')
                if payment_method_cheque_id:
                    return_list.append(payment_method_bank_transfer_id[1])
            except Exception as e:
                pass
        config_setting_obj = self.env[
            'res.config.settings'].sudo().get_values()
        self.state = "new"
        self.commission = config_setting_obj[
            "global_commission"] if config_setting_obj.get("global_commission") else False
        self.warehouse_id = config_setting_obj[
            "mp_default_warehouse_id"] if config_setting_obj.get("mp_default_warehouse_id") else False
        self.location_id = config_setting_obj[
            "warehouse_location_id"] if config_setting_obj.get("warehouse_location_id") else False
        self.auto_product_approve = config_setting_obj[
            "auto_product_approve"] if config_setting_obj.get("auto_product_approve") else False
        self.seller_payment_limit = config_setting_obj[
            "seller_payment_limit"] if config_setting_obj.get("seller_payment_limit") else 0
        self.next_payment_request = config_setting_obj[
            "next_payment_requset"] if config_setting_obj.get("next_payment_requset") else 0
        self.auto_approve_qty = config_setting_obj[
            "auto_approve_qty"] if config_setting_obj.get("auto_approve_qty") else False
        self.payment_method = return_list

    # CRUD methods (and name_get, name_search, ...) overrides

    @api.model
    def create(self, vals):
        if vals.get('url_handler'):
            if not re.match('^[a-zA-Z0-9-_]+$', vals.get('url_handler')) or re.match('^[-_][a-zA-Z0-9-_]*$', vals.get('url_handler')) or re.match('^[a-zA-Z0-9-_]*[-_]$', vals.get('url_handler')):
                raise UserError(_("Please enter URL handler correctly!"))
            sameurl = self.search([('url_handler', '=', vals.get('url_handler'))])
            if sameurl:
                raise UserError(_("Url already registered!"))
            vals["url_handler"] = vals.get('url_handler').lower().replace(" ","-") or ""
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        new_seller = False
        if not self.env.user.has_group('odoo_marketplace.marketplace_manager_group'):
            for res in manager_fields:
                if res in vals:
                    vals.pop(res)
        change_state_to = False
        for rec in self:
            if rec.seller:
                if rec.state != "approved" and vals.get("state", "") == "approved":
                    change_state_to = vals.get("state", False)
                if vals.get("state", "") in ["denied", "pending"]:
                    if rec.state == "new":
                        new_seller = True
                    change_state_to = vals.get("state", False)
                if vals.get("commission", 0) < 0 or vals.get("commission", 0) >= 100:
                    raise Warning(_("Commission should be greater than 0 and less than 100."))
                if vals.get("seller_payment_limit", 0) < 0 :
                    raise Warning(_("Amount Limit can't be negative."))
                if vals.get("next_payment_request", 0) < 0:
                    raise Warning(_("Minimum Gap can't be negative."))
                if vals.get('url_handler'):
                    if not re.match('^[a-zA-Z0-9-_]+$', vals.get('url_handler')) or re.match('^[-_][a-zA-Z0-9-_]*$', vals.get('url_handler')) or re.match('^[a-zA-Z0-9-_]*[-_]$', vals.get('url_handler')):
                        raise UserError(_("Please enter URL handler correctly!"))
                    sameurl = self.search([ ('url_handler', '=', vals['url_handler']) , ('id', '!=', rec.id)])
                    if sameurl:
                        raise UserError(_("Url already registered!"))
                    vals["url_handler"] = (vals.get('url_handler').lower().replace(" ","-") or rec.url_handler.lower().replace(" ","-") or "") if vals.get('url_handler') else ""
                    # vals['url'] = base_url + (vals.get('url_handler') or "")
        res = super(ResPartner, self).write(vals)
        for rec in self:
            if rec.seller and change_state_to == "approved":
                rec.change_seller_group_and_send_mail()
            elif rec.seller and vals.get("state", "") in ["denied", "pending"]:
                if new_seller:
                    rec.with_context(new_to_pending=True).change_seller_group_and_send_mail()
                else:
                    rec.change_seller_group_and_send_mail()
        return res

    @api.multi
    def get_seller_global_settings(self, config_setting_obj):
        self.ensure_one()
        warehouse_id = config_setting_obj.get("mp_default_warehouse_id")
        warehouse_id = [warehouse_id] if warehouse_id else []
        location_id = config_setting_obj.get("warehouse_location_id")
        location_id = [location_id] if location_id else []
        mp_default_warehouse_id = self.env["stock.warehouse"].browse(warehouse_id)
        warehouse_location_id = self.env["stock.location"].browse(location_id)
        global_settings = {
            "commission": config_setting_obj.get("global_commission"),
            "warehouse_id": mp_default_warehouse_id.name_get()[0] if mp_default_warehouse_id else None,
            "location_id": warehouse_location_id.name_get()[0] if location_id else None,
            "auto_product_approve": config_setting_obj.get("auto_product_approve"),
            "seller_payment_limit": config_setting_obj.get("seller_payment_limit"),
            "next_payment_request": config_setting_obj.get("next_payment_requset"),
            "auto_approve_qty": config_setting_obj.get("auto_approve_qty"),
        }
        return global_settings

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        result = super(ResPartner, self).read(fields=fields, load=load)
        irmodule_obj = self.env['ir.module.module']
        module_installed = irmodule_obj.sudo().search([('name', 'in', ['odoo_marketplace']), ('state', 'in', ['installed'])])
        if module_installed:
            config_setting_obj = self.env['res.config.settings'].sudo().get_values()
            for seller_vals in result:
                seller = self.browse(seller_vals.get('id'))
                if seller.seller and seller.state in ['approved','pending'] and not seller.set_seller_wise_settings:
                    global_settings = seller.get_seller_global_settings(config_setting_obj)
                    vals = {g_field : global_settings.get(g_field) for g_field in global_settings.keys() if g_field in seller_vals.keys()}
                    seller_vals.update(vals)
                    seller._cache.update(seller._convert_to_cache(vals, validate=False))
        return result


    # Action methods

    @api.one
    def approve(self):
        if self.seller:
            self.state = "approved"

    @api.one
    def deny(self):
        if self.seller:
            self.state = "denied"

    @api.one
    def set_to_pending(self):
        if self.seller:
            config_setting_obj = self.env['res.config.settings'].sudo().get_values()
            if config_setting_obj.get("auto_approve_seller", False):
                self.sudo().approve()
            else:
                self.sudo().state = "pending"
                # self.status_msg = config_setting_obj.get("seller_pending_status_msg", "Thank you for seller request, your request has been already sent for approval we'll process your request as soon as possible.")

    @api.multi
    def toggle_website_published(self):
        """ Inverse the value of the field ``website_published`` on the records in ``self``. """
        for record in self:
            record.website_published = not record.website_published

    def set_sequence_top(self):
        self.website_sequence = self.sudo().search([], order='website_sequence desc', limit=1).website_sequence + 1

    def set_sequence_bottom(self):
        self.website_sequence = self.sudo().search([], order='website_sequence', limit=1).website_sequence - 1

    def set_sequence_up(self):
        previous_seller = self.sudo().search(
            [('website_sequence', '>', self.website_sequence), ('website_published', '=', self.website_published)],
            order='website_sequence', limit=1)
        if previous_seller:
            previous_seller.website_sequence, self.website_sequence = self.website_sequence, previous_seller.website_sequence
        else:
            self.set_sequence_top()

    def set_sequence_down(self):
        next_seller = self.search([('website_sequence', '<', self.website_sequence), ('website_published', '=', self.website_published)], order='website_sequence desc', limit=1)
        if next_seller:
            next_seller.website_sequence, self.website_sequence = self.website_sequence, next_seller.website_sequence
        else:
            return self.set_sequence_bottom()

    @api.multi
    def enable_product_variant_group(self):
        for obj in self:
            user = self.env["res.users"].sudo().search(
                [('partner_id', '=', obj.id)])
            if user:
                # Add user to product variant group
                group = self.env.ref('product.group_product_variant')
                if group:
                    group.sudo().write({"users": [(4, user.id, 0)]})

    @api.multi
    def disable_product_variant_group(self):
        for obj in self:
            user = self.env["res.users"].sudo().search(
                [('partner_id', '=', obj.id)])
            if user:
                # Remove user from product variant group
                group = self.env.ref('product.group_product_variant')
                if group:
                    group.sudo().write({"users": [(3, user.id, 0)]})

    @api.multi
    def action_seller_sol(self):
        self.ensure_one()
        action = self.env.ref('odoo_marketplace.wk_seller_slae_order_line_action')
        list_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'odoo_marketplace.wk_seller_product_order_line_tree_view')
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'odoo_marketplace.wk_seller_product_order_line_form_view')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'res_model': action.res_model,
            'domain': "[('marketplace_seller_id','=',%s), ('state','not in',('draft','sent'))]" % self._ids[0],
        }

    # Business methods

    @api.multi
    def change_seller_group(self, set_to_group=None):
        """ param: set_to_group should be string, value must be 'not_seller' or 'seller' only. """

        if not set_to_group:
            return
        login_user_obj = self.env.user
        if not login_user_obj.has_group('odoo_marketplace.marketplace_officer_group'):
            _logger.info(_("~~~~~~~~~~You are not an autorized user to change seller account access. Please contact your administrator. "))
            raise UserError(_("You are not an autorized user to change seller account access. Please contact your administrator. "))
        for seller in self.filtered(lambda o: o.seller == True):
            seller_user = self.env["res.users"].sudo().search([('partner_id', '=', seller.id)])
            pending_seller_group_obj = self.env.ref('odoo_marketplace.marketplace_draft_seller_group')
            seller_group_obj = self.env.ref('odoo_marketplace.marketplace_seller_group')
            if set_to_group == "seller":
                #First check seller user realy belongs to draft seller group(marketplace_draft_seller_group) or not
                if seller_user.has_group("odoo_marketplace.marketplace_draft_seller_group"):
                    # Remove seller user from draft seller group(marketplace_draft_seller_group)
                    pending_seller_group_obj.sudo().write({"users": [(3, seller_user.id, 0)]})
                    # Add seller user to seller group(marketplace_seller_group)
                    seller_group_obj.sudo().write({"users": [(4, seller_user.id, 0)]})
                else:
                    _logger.info(_("~~~~~~~~~~Seller does not belongs to draft seller group. So you can't change seller group to seller group."))
            elif set_to_group == "not_seller":
                #First check seller user realy belongs to seller group(marketplace_seller_group) or not
                if seller_user.has_group("odoo_marketplace.marketplace_seller_group"):
                    # Remove seller user from seller group(marketplace_seller_group)
                    seller_group_obj.write({"users": [(3, seller_user.id, 0)]})
                    # Add seller user to draft seller group(marketplace_draft_seller_group)
                    pending_seller_group_obj.write({"users": [(4, seller_user.id, 0)]})

    @api.one
    def notify_via_mail_to_seller(self, mail_templ_id):
        """ """
        if not mail_templ_id:
            return False
        template_obj = self.env['mail.template'].browse(mail_templ_id)
        template_obj.send_mail(self.id, True)

    @api.one
    def change_seller_group_and_send_mail(self):
        """ Call this method to change seller group and send mail to seller when state has been set to 'approved'.
            param: string value can be ('pending', 'denied', 'approved'). Action will be performed for 'pending', 'denied', 'approved' values by asuming that one of the these value has been set current state.
        """

        if self.seller and self.state == "approved":
            #Change seller to approve seller group(marketplace_seller_group)
            self.change_seller_group(set_to_group="seller")

            #Send mail to admin/seller on seller approval
            config_setting_obj = self.env['res.config.settings'].sudo().get_values()
            if config_setting_obj.get("enable_notify_admin_on_seller_approve_reject", False) and config_setting_obj.get("notify_admin_on_seller_approve_reject_m_tmpl_id", False):
                # Notify to admin by admin on new seller creation
                self.notify_via_mail_to_seller(config_setting_obj.get("notify_admin_on_seller_approve_reject_m_tmpl_id", False))
            if config_setting_obj.get("enable_notify_seller_on_approve_reject", False) and config_setting_obj.get("notify_seller_on_approve_reject_m_tmpl_id", False):
                # Notify to Seller by admin on new seller creation
                self.notify_via_mail_to_seller(config_setting_obj.get("notify_seller_on_approve_reject_m_tmpl_id", False))
        elif self.seller and self.state in ["pending", "denied"]:
            #Change seller to draft seller group(marketplace_draft_seller_group)
            self.env["product.template"].disable_seller_all_products(self.id)
            self.env["marketplace.stock"].disable_seller_all_inventory_requests(self.id)
            self.change_seller_group(set_to_group="not_seller")

            if self._context.get("new_to_pending", False):
                #Send mail to admin/seller on seller approval
                config_setting_obj = self.env['res.config.settings'].sudo().get_values()
                if config_setting_obj.get("enable_notify_admin_4_new_seller", False) and config_setting_obj.get("notify_admin_4_new_seller_m_tmpl_id", False):
                    # Notify to admin by admin on new seller creation
                    self.notify_via_mail_to_seller(config_setting_obj.get(
                        "notify_admin_4_new_seller_m_tmpl_id", False))
                if config_setting_obj.get("enable_notify_seller_4_new_seller", False) and config_setting_obj.get("notify_seller_4_new_seller_m_tmpl_id", False):
                    # Notify to Seller by admin on new seller creation
                    self.notify_via_mail_to_seller(config_setting_obj.get("notify_seller_4_new_seller_m_tmpl_id", False))
            else:
                #Send mail to admin/seller on seller approval
                config_setting_obj = self.env['res.config.settings'].sudo().get_values()
                if config_setting_obj.get("enable_notify_admin_on_seller_approve_reject", False) and config_setting_obj.get("notify_admin_on_seller_approve_reject_m_tmpl_id", False):
                    # Notify to admin by admin on new seller creation
                    self.notify_via_mail_to_seller(config_setting_obj.get("notify_admin_on_seller_approve_reject_m_tmpl_id", False))
                if config_setting_obj.get("enable_notify_seller_on_approve_reject", False) and config_setting_obj.get("notify_seller_on_approve_reject_m_tmpl_id", False):
                    # Notify to Seller by admin on new seller creation
                    self.notify_via_mail_to_seller(config_setting_obj.get("notify_seller_on_approve_reject_m_tmpl_id", False))
        else:
            _logger.info(_("Seller is not in approved, denied, pending state. So you can't change seller group and notify to seller"))
        return True

    @api.multi
    def seller_request_for_apyment(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'seller.payment.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': 'id_of_the_wizard',
            'target': 'new',
        }

    @api.multi
    def create_seller_shop(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'seller.shop',
            'view_type': 'form',
            'view_mode': 'form',
            'flags': {'form': {'action_buttons': True, 'reload_on_button': True}},
            "context": {"default_seller_id": self._context.get("active_id")},
            'target': 'new',
        }

    # Methods used in seller review process
    @api.multi
    def _set_avg_rating(self):
        """ """
        add = 0.0
        avg = 0.0
        for obj in self:
            if obj.seller_review_ids:
                for reviews_obj in obj.seller_review_ids:
                    add += reviews_obj.rating
                avg = add / len(obj.seller_review_ids)
            obj.average_rating = (round(decimal.Decimal(abs(avg)), 2))

    def fetch_active_review(self, seller_id):
        if seller_id:
            review_ids = self.env["seller.review"].search(
                [('marketplace_seller_id', '=', seller_id), ('website_published', '=', True)])
            return review_ids
        else:
            return []

    def fetch_active_review2(self, seller_id, offset=0, limit=False, sort_by="recent", filter_by=-1):
        # By default recent reviews is searched
        if filter_by == -1:
            review_ids = self.env["seller.review"].search([('marketplace_seller_id', '=', seller_id), (
                'website_published', '=', True)], order="helpful desc" if sort_by == "most_helpful" else "create_date desc")
        if filter_by == 1:
            review_ids = self.env["seller.review"].search([('marketplace_seller_id', '=', seller_id), ('website_published', '=', True), (
                'rating', '=', 1)], order="helpful desc" if sort_by == "most_helpful" else "create_date desc")
        if filter_by == 2:
            review_ids = self.env["seller.review"].search([('marketplace_seller_id', '=', seller_id), ('website_published', '=', True), (
                'rating', '=', 2)], order="helpful desc" if sort_by == "most_helpful" else "create_date desc")
        if filter_by == 3:
            review_ids = self.env["seller.review"].search([('marketplace_seller_id', '=', seller_id), ('website_published', '=', True), (
                'rating', '=', 3)], order="helpful desc" if sort_by == "most_helpful" else "create_date desc")
        if filter_by == 4:
            review_ids = self.env["seller.review"].search([('marketplace_seller_id', '=', seller_id), ('website_published', '=', True), (
                'rating', '=', 4)], order="helpful desc" if sort_by == "most_helpful" else "create_date desc")
        if filter_by == 5:
            review_ids = self.env["seller.review"].search([('marketplace_seller_id', '=', seller_id), ('website_published', '=', True), (
                'rating', '=', 5)], order="helpful desc" if sort_by == "most_helpful" else "create_date desc")
        # review_ids = self.env["seller.review"].search([('marketplace_seller_id','=',seller_id),('website_published','=',True)])
        return_obj = []
        if review_ids and offset < len(review_ids):
            while offset < len(review_ids) and limit != 0:
                return_obj.append(review_ids[offset])
                offset += 1
                limit -= 1
            _logger.info("==========review_ids=%r==offset==============================",limit)
            return return_obj
        else:
            return []

    def avg_review(self):
        val = 0.0
        length = 0.0
        if self._ids:
            reviews_obj = self.fetch_active_review(self._ids[0])
            if reviews_obj:
                for obj in reviews_obj:
                    val += float(obj.rating)
                    length = float(len(reviews_obj))
                return round((val / length), 1)
        return 0

    @api.one
    def temp_review(self):
        value = self.avg_review()
        if value:
            dec = int(value)
            frac = int((value - dec) / .1)
            if frac in [1, 2]:
                frac = 2
            elif frac in [3, 4]:
                frac = 4
            elif frac in [5, 6]:
                frac = 6
            elif frac in [7, 8, 9]:
                frac = 8
            return [dec, frac]
        return [0, 0]

    @api.multi
    def fetch_user_vote(self, seller_review_id):
        like_dislike = self.env["review.help"]
        review_help_ids = like_dislike.search(
            [('customer_id', '=', self._uid), ('seller_review_id', '=', seller_review_id)])
        if review_help_ids:
            result = [True if review_help_ids[0].review_help == "yes" else False,
                      True if review_help_ids[0].review_help == "no" else False]
            return result
        return [False, False]

    @api.model
    def get_review_current_time(self, seller_review_id):
        review_pool = self.env["seller.review"]
        if seller_review_id:
            seller_review_obj = review_pool.browse(seller_review_id)
            # iso_format = datetime.strptime(
            #     seller_review_obj.create_date, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%dT%H:%M:%SZ')
            iso_format = seller_review_obj.create_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            return iso_format

    @api.multi
    def action_avg_seller_review_fun(self):
        self.ensure_one()
        action = self.env.ref('odoo_marketplace.action_seller_review')
        list_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'odoo_marketplace.mp_seller_review_tree_view_webkul2')
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'odoo_marketplace.mp_seller_review_form_view_webkul2')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'res_model': action.res_model,
            'domain': "[('marketplace_seller_id','=',%s)]" % self._ids[0],
        }

    def total_star_count(self, no_of_star):
        if not no_of_star:
            return 0
        review_ids = self.env["seller.review"].search(
            [('marketplace_seller_id', '=', self.id), ('website_published', '=', True), ("rating", "=", no_of_star)])
        return len(review_ids.ids) if review_ids else 0

    def total_active_recommendation(self):
        return_list = []
        recommendation_ids = self.env[
            "seller.recommendation"].search([('state', '=', "pub"),("seller_id","=",self.id)])
        recommendation_yes_ids = self.env["seller.recommendation"].search(
            [('state', '=', "pub"), ("recommend_state", "=", "yes"),("seller_id","=",self.id)])
        yes_percentage = len(recommendation_yes_ids.ids) * 100 / \
            len(recommendation_ids.ids) if recommendation_ids else 0
        return_list.append(len(recommendation_ids.ids)
                           if recommendation_ids else 0)
        return_list.append(yes_percentage)
        return return_list

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(ResPartner, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        manager_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_officer_group')[1]
        groups_ids = self.env.user.sudo().groups_id.ids

        if manager_group not in groups_ids and result.get("toolbar", False):
            result["toolbar"] = {}
        return result

    def seller_sales_count(self):
        # Calculate seller total sales count
        sales_count = 0
        all_products = self.env['product.template'].sudo().search(
            [("marketplace_seller_id", "=", self.sudo().id)])
        for prod in all_products:
            sales_count += prod.sales_count
        return sales_count

    def seller_products_count(self):
        # Calculate seller total products count
        sales_count = 0
        all_products = self.env['product.template'].sudo().search(
            [("marketplace_seller_id", "=", self.sudo().id), ("status",'=','approved'),('website_published', '=', True)])
        return len(all_products)

    @api.multi
    def register_partner_as_a_seller(self):
        for rec in self:
            current_user = rec.env['res.users'].search([('partner_id','=',rec.id)])
            context = dict(rec._context) or {}
            context['active_id'] = rec.id
            if current_user:
                context['user_id'] = current_user.id
            return {
                'name':'Register Partner As a Seller',
                'type':'ir.actions.act_window',
                'res_model':'seller.resistration.wizard',
                'view_mode':'form',
                'view_type':'form',
                'view_id':rec.env.ref('odoo_marketplace.seller_registration_wizard_form').id,
                'context' : context,
                'target':'new',
            }


class SellerSocialMedia(models.Model):
    _description = " Model to manage sellers social media links."
    _name = "seller.social.media.link"
    _rec_name = "social_media_id"

    # Fields declaration

    social_media_id = fields.Many2one("social.media", "Profile Name", required=True)
    social_profile_id = fields.Char("Profile Id", required=True, help="Social media profile id.")
    seller_id = fields.Many2one("res.partner")
    wk_website_published = fields.Boolean("Published")
    complete_url = fields.Char(compute="_get_complete_profile_url", string="Profile URL")

    # compute and search field methods, in the same order of fields declaration
    @api.depends("social_media_id", "social_media_id.base_url", "social_profile_id")
    @api.multi
    def _get_complete_profile_url(self):
        for obj in self:
            url = False
            if obj.social_media_id.base_url:
                if obj.social_media_id.base_url.endswith('/'):
                    url = obj.social_media_id.base_url + str(obj.social_profile_id) if obj.social_profile_id else ""
                else:
                    url = obj.social_media_id.base_url + '/' + str(obj.social_profile_id) if obj.social_profile_id else ""
            obj.complete_url = url

    # Constraints and onchanges

    @api.onchange("social_media_id")
    def onchange_profile_id(self):
        if self.social_media_id:
            self._get_complete_profile_url()

    # Action methods

    @api.multi
    def toggle_website_published(self):
        """ Inverse the value of the field ``wk_website_published`` on the records in ``self``. """
        for record in self:
            record.wk_website_published = not record.wk_website_published

    # Business methods

    @api.multi
    def visit_profile(self):
        self.ensure_one()
        url = False
        if self.social_media_id.base_url:
            url = self.social_media_id.base_url + str(self.social_profile_id) if self.social_profile_id else ""
        else:
            raise Warning(_("Base Url not found."))
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
            'res_id': self.id,
        }

class SocialMedia(models.Model):
    _name = "social.media"
    _description = " Model to manage social media."

    # Fields declaration

    name = fields.Char("Name", required=True)
    image = fields.Binary("Social Media Image")
    base_url = fields.Char("Base URL", required=True, help="Social media site complete url.")
