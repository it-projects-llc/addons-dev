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
from odoo.exceptions import UserError
import re

class SellerShopStyle(models.Model):
    _name = "seller.shop.style"
    _description = "Seller Shop"

    name = fields.Char(string='Style Name', required=True)
    html_class = fields.Char(string='HTML Classes')


class SellerShop(models.Model):
    _inherit = ['website.published.mixin', 'mail.thread']
    _name = 'seller.shop'
    _description = "Seller Shop"

    @api.multi
    def _get_page_url(self):
        for obj in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            base_url = base_url + "/seller/shop/"
            url_handler = str(obj.id) if not obj.url_handler else obj.url_handler
            obj.url = base_url + url_handler

    @api.depends("seller_id")
    def _get_seller_products(self):
        for rec in self:
            product_objs = self.env["product.template"].search([('sale_ok', '=', True), (
                'status', '=', 'approved'), ("marketplace_seller_id", "=", rec.seller_id.id)])
            if product_objs:
                rec.seller_product_ids = product_objs.ids

    @api.depends("seller_product_ids")
    def _calculate_tot_products(self):
        for rec in self:
            rec.total_product = len(rec.seller_product_ids.ids)

    def _default_website_sequence(self):
        self._cr.execute("SELECT MIN(website_sequence) FROM %s" % self._table)
        min_sequence = self._cr.fetchone()[0]
        return min_sequence and min_sequence - 1 or 10

    name = fields.Char(string="Shop Name",  translate=True, copy=False)
    shop_logo = fields.Binary(string="Image",
                              help="This field holds the image used as image for the product, limited to 1024x1024px.")
    shop_banner = fields.Binary(string="Shop Banner")
    description = fields.Text(string="Description",  translate=True)
    street = fields.Char(string='Street', copy=False)
    street2 = fields.Char(string='Street2', copy=False)
    zip = fields.Char(string='Zip', size=24, change_default=True, copy=False)
    city = fields.Char(string='City', copy=False)
    state_id = fields.Many2one(
        "res.country.state", string='State', ondelete='restrict', copy=False)
    country_id = fields.Many2one(
        'res.country', string='Country', ondelete='restrict', copy=False)
    email = fields.Char(string='Email', copy=False)
    phone = fields.Char(string='Phone', copy=False)
    fax = fields.Char(string='Fax', copy=False)
    shop_mobile = fields.Char(string="Mobile Number", copy=False)
    shop_tag_line = fields.Char(string="Tag Line", copy=False, size=100)
    seller_product_ids = fields.Many2many("product.template", "shop_product_table",
                                          "shop_id", "product_id", string="Products", compute="_get_seller_products")
    seller_id = fields.Many2one(
        "res.partner", string="Seller", domain="[('seller','=', True)]", required=True)
    sequence = fields.Integer(
        string='Sequence', help='Gives the sequence order when displaying a product list')
    active = fields.Boolean(
        'Active', default=True)
    state = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'), (
        'denied', 'Denied')], related="seller_id.state", string="Shop Status", copy=False)
    color = fields.Integer(string="Color")
    shop_t_c = fields.Html(string="Terms & Conditions", copy=False)
    total_product = fields.Integer(
        compute="_calculate_tot_products", string="Total Product")

    # Seller shop/profile releted field
    set_seller_wise_settings = fields.Boolean(
        string="Override default shop settings")

    website_size_x = fields.Integer('Size X', default=1)
    website_size_y = fields.Integer('Size Y', default=1)
    website_style_ids = fields.Many2many('seller.shop.style', string='Styles')
    website_sequence = fields.Integer('Website Sequence', help="Determine the display order in the Website E-commerce",
                                      default=lambda self: self._default_website_sequence())

    url = fields.Char(string="URL", compute=_get_page_url)
    url_handler = fields.Char("Url Handler", required=True, help="Unique Shop URL handeler...", copy=False)

    _sql_constraints = [('seller_id_uniqe', 'unique(seller_id)', _('This seller is already assign to another shop.')),
                        ('url_handler_unique', 'unique(url_handler)', _('Url Handler must be unique for the shop. Entered URL handler has been already used.')),
                        ('name_unique', 'unique(name)', _('Shop name has been already used. Shop name must be unique so change shop name.'))]

    @api.onchange('state_id')
    def on_change_state_id(self):
        if self.state_id and self.state_id.country_id:
            self.country_id = self.state_id.country_id

    @api.onchange('name')
    def on_change_name(self):
        if self.name and not self.url_handler:
            self.url_handler = self.name.lower().replace(' ', '-') or ""

    @api.model
    def create(self, vals):
        if vals.get('url_handler'):
            if not re.match('^[a-zA-Z0-9-_]+$', vals.get('url_handler')) or re.match('^[-_][a-zA-Z0-9-_]*$', vals.get('url_handler')) or re.match('^[a-zA-Z0-9-_]*[-_]$', vals.get('url_handler')):
                raise UserError(_("Please enter URL handler correctly!"))
        res = super(SellerShop, self).create(vals)
        if vals.get("seller_id") and res:
            self.env["res.partner"].browse(vals.get("seller_id")).write({"seller_shop_id": res.id})
        res.save()
        return res

    @api.multi
    def write(self, vals):
        for obj in self:
            if vals.get('url_handler'):
                if not re.match('^[a-zA-Z0-9-_]+$', vals.get('url_handler')) or re.match('^[-_][a-zA-Z0-9-_]*$', vals.get('url_handler')) or re.match('^[a-zA-Z0-9-_]*[-_]$', vals.get('url_handler')):
                    raise UserError(_("Please enter URL handler correctly!"))
            if vals.get("seller_id"):
                self.env["res.partner"].browse(vals.get("seller_id")).write({"seller_shop_id": obj.id})
        res = super(SellerShop, self).write(vals)
        return res

    @api.multi
    def save(self):
        self.ensure_one()
        seller_obj = self.env["res.partner"].browse(
            self._context.get("active_id"))
        if seller_obj:
            seller_obj .write({"seller_shop_id": self.id})

    def seller_sales_count(self):
        # Calculate seller total sales count
        sales_count = 0
        all_products = self.env['product.template'].sudo().search(
            [("marketplace_seller_id", "=", self.seller_id.sudo().id)])
        for prod in all_products:
            sales_count += prod.sales_count
        return sales_count

    def set_sequence_top(self):
        self.website_sequence = self.sudo().search([], order='website_sequence desc', limit=1).website_sequence + 1

    def set_sequence_bottom(self):
        self.website_sequence = self.sudo().search([], order='website_sequence', limit=1).website_sequence - 1

    def set_sequence_up(self):
        previous_shop = self.sudo().search(
            [('website_sequence', '>', self.website_sequence), ('website_published', '=', self.website_published)],
            order='website_sequence', limit=1)
        if previous_shop:
            previous_shop.website_sequence, self.website_sequence = self.website_sequence, previous_shop.website_sequence
        else:
            self.set_sequence_top()

    def set_sequence_down(self):
        next_shop = self.search([('website_sequence', '<', self.website_sequence), ('website_published', '=', self.website_published)], order='website_sequence desc', limit=1)
        if next_shop:
            next_shop.website_sequence, self.website_sequence = self.website_sequence, next_shop.website_sequence
        else:
            return self.set_sequence_bottom()
