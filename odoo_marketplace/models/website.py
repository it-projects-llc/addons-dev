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


from odoo import api, fields, models


class Website(models.Model):
	_inherit = 'website'

	mp_product_count = fields.Boolean(
		string="Show seller's product count on website.")
	mp_sale_count = fields.Boolean(string="Show seller's sales count on website.")
	mp_shipping_address = fields.Boolean(
		string="Show seller's shipping address on website.")
	mp_seller_since = fields.Boolean(string="Show seller since Date on website.")
	mp_seller_t_c = fields.Boolean(
		string="Show seller's Terms & Conditions on website.")
	mp_seller_contact_btn = fields.Boolean(
		string='Show "Contact Seller" Button on website.')
	mp_seller_review = fields.Boolean(
		string='Show Seller Review on website.')
	mp_return_policy = fields.Boolean(
		string="Show seller's Retrun Policy on website.")
	mp_shipping_policy = fields.Boolean(
		string="Show Seller's Shipping Policy on website.")
	mp_recently_product = fields.Integer(
		string="# of products for recently added products menu. ")
	mp_review_load_no = fields.Integer(
		string="No. of Reviews to load", help="Set default numbers of review to show on website.")
	mp_review_auto_publish = fields.Boolean(
		string="Auto Publish", help="Publish Customer's review automatically.")
	mp_show_seller_list = fields.Boolean(
		string='Show Sellers List on website.')
	mp_show_seller_shop_list = fields.Boolean(
		string='Show Seller Shop List on website.')
	mp_show_become_a_seller = fields.Boolean("Show Become a Seller button on Account Home Page")
	mp_term_and_condition = fields.Html(string="Terms & Conditions", translate=True)
	mp_message_to_publish = fields.Text(
		string="Review feedback message", help="Message to Customer on review publish.", translate=True)
	mp_sell_page_label = fields.Char(
		string="Sell Link Label", default="Sell", translate=True)
	mp_sellers_list_label = fields.Char(
		string="Seller List Link Label", default="Sellers List", translate=True)
	mp_seller_shop_list_label = fields.Char(
		string="Seller Shop List Link Label", default="Seller Shop List", translate=True)
	mp_landing_page_banner = fields.Binary(string="Landing Page Banner")
	mp_seller_new_status_msg = fields.Text(
		string="For New Status", default="Thank you for registering with us, to enjoy the benefits of our marketplace fill all your details and request for approval.", translate=True)
	mp_seller_pending_status_msg = fields.Text(
		string="For Pending Status", default="Thank you for seller request, your request has been already sent for approval we'll process your request as soon as possible.", translate=True)
	mp_show_sell_menu_header = fields.Boolean(string="Show Sell menu in header")
	mp_show_sell_menu_footer = fields.Boolean(string="Show Sell menu in footer")
	# mp_seller_denied_status_msg = fields.Text(
	# 	string="For Denied Status", default="Sorry To Say! Your seller account has been denied now.", translate=True)

	@api.model
	def get_group_mp_shop_allow(self):
		return self.env['ir.default'].sudo().get('res.config.settings', 'group_mp_shop_allow')

	@api.model
	def get_mp_ajax_seller_countries(self):
		countries = self.env['res.country'].sudo().search([])
		return  countries
