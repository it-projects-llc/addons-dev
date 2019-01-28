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
from random import randint

color_count = 10
colors_dict = {0: "#EF5350", 1: "#4CAF50", 2: "#7E57C2", 3: "#FF7043", 4: "#FF4081", 5: "#5fcbef", 6: "#63d6d1", 7: "#fba565", 8: "#8064fa", 9: "#daab85", 10: "#e06a6e",
               11: "#EC407A", 12: "#AB47BC", 13: "#42A5F5", 14: "#5C6BC0", 15: "#DCE775", 16: "#66BB6A", 17: "#9CCC65", 18: "#40C4FF", 19: "#8D6E63", 20: "#B0BEC5", }


class SellerReview(models.Model):
    _name = "seller.review"
    _rec_name = 'title'
    _description = "Seller Review"
    _inherit = ['website.published.mixin','mail.thread']

    _order = "website_published desc, create_date desc"
    _mail_post_access = 'read'

    @api.model
    def create(self, vals):
        if vals.get('rating', False):
            if vals['rating'] <= 0:
                raise UserError('Warning Rating must be more than zero')
            if vals['rating'] > 5:
                raise UserError('Warning Rating can not be more than 5')
        return super(SellerReview, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('rating', False):
            if vals['rating'] <= 0:
                raise UserError('Warning Rating must be more than zero')
            if vals['rating'] > 5:
                raise UserError('Warning Rating can not be more than 5')
        return super(SellerReview, self).write(vals)

    @api.model
    def _get_mail(self):
        res_obj = self.env['res.users'].browse(self._uid)
        email = res_obj.email
        return email

    @api.model
    def _get_image(self):
        res_obj = self.env['res.users'].browse(self._uid)
        image = res_obj.image
        return image

    @api.model
    def _get_auto_website_published(self):
        config_setting_obj = self.env[
            'res.config.settings'].sudo().get_values()
        if config_setting_obj.get('review_auto_publish', False):
            return config_setting_obj['review_auto_publish']
        else:
            return False

    @api.depends("review_help_ids")
    @api.multi
    def _set_total_helpful(self):
        """ """
        for obj in self:
            review_help_ids = obj.env["review.help"].search(
                [('review_help', '=', "yes"), ('seller_review_id', '=', obj.id)])
            obj.helpful = len(review_help_ids)

    @api.multi
    def _get_rating(self):
        """ """
        for obj in self:
            obj.rating2 = obj.rating

    @api.depends("review_help_ids")
    @api.multi
    def _set_total_not_helpful(self):
        """ """
        for obj in self:
            review_help_ids = obj.env["review.help"].search(
                [('review_help', '=', "no"), ('seller_review_id', '=', obj.id)])
            obj.not_helpful = len(review_help_ids)

    @api.multi
    def _set_total_votes(self):
        """ """
        for obj in self:
            review_help_ids = obj.env["review.help"].search(
                [('seller_review_id', '=', obj.id)])
            obj.total_votes = len(review_help_ids)

    @api.depends('website_published')
    def _get_value_website_published(self):
        for record in self:
            if record.website_published:
                record.state = 'pub'
            else:
                record.state = 'unpub'

    @api.model
    def _get_default_color(self):
        color_index = randint(0, 20)
        return colors_dict[color_index]

    title = fields.Char(string='Title', translate=True, required=True, copy=False)
    active = fields.Boolean(string="Active", default=True)
    msg = fields.Text(string='Message', required=True, translate=True, copy=False)
    rating = fields.Integer(string='Rating', default=1, copy=False)
    rating2 = fields.Integer(compute="_get_rating", string="Rating2", copy=False)
    email = fields.Char(string='Email', default=_get_mail, copy=False)
    website_published = fields.Boolean(
        'Available on the website', copy=False, default=_get_auto_website_published)
    marketplace_seller_id = fields.Many2one('res.partner', string='Seller', domain=[('seller', '=', True)], copy=False)
    create_date = fields.Datetime(string='Created Date')
    helpful = fields.Integer(compute='_set_total_helpful',
                             string='Helpful', store=True)
    not_helpful = fields.Integer(
        compute='_set_total_not_helpful', string='Not Helpful', store=True)
    total_votes = fields.Integer(
        compute='_set_total_votes', string='Lotal Votes')
    review_help_ids = fields.One2many(
        'review.help', 'seller_review_id', string="Helpful/Not Helpful")
    state = fields.Selection([('pub', 'Published'), ('unpub', 'Unpublished')],
                             compute='_get_value_website_published', store=True, translate=True, copy=False)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", default=lambda self: self.env.user.partner_id, domain=[('customer', '=', True)])
    color = fields.Char(string="Color", default=_get_default_color)
    website_message_ids = fields.One2many(
        'mail.message', 'res_id',
        domain=lambda self: ['&', ('model', '=', self._name), ('message_type', '=', 'comment')],
        string='Website Seller Review Comments',
    )

    @api.onchange("partner_id")
    def on_change_customer(self):
        if self.partner_id:
            self.email = self.partner_id.email

    @api.multi
    def action_review_helfull_fun(self):
        self.ensure_one()
        action = self.env.ref('odoo_marketplace.action_reviews_helpful_list')
        list_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'odoo_marketplace.seller_review_help_tree_view')
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'odoo_marketplace.wk_seller_review_help_Form_view')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'res_model': action.res_model,
            'domain': "[('review_help','=','yes'),('seller_review_id','=',%s)]" % self._ids[0],
        }

    @api.multi
    def action_review_not_helpful_fun(self):
        self.ensure_one()
        action = self.env.ref(
            'odoo_marketplace.action_reviews_not_helpful_list')
        list_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'odoo_marketplace.seller_review_help_tree_view')
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'odoo_marketplace.wk_seller_review_help_Form_view')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': "{'default_seller_review_id': " + str(self._ids[0]) + "}",
            'res_model': action.res_model,
            'domain': "[('review_help','=','no'),('seller_review_id','=',%s)]" % self._ids[0],
        }

    @api.multi
    def toggle_website_published(self):
        """ Inverse the value of the field ``website_published`` on the records in ``self``. """
        for record in self:
            record.website_published = not record.website_published

class ReviewHelp(models.Model):
    _name = "review.help"
    _description = "Seller review help"
    _order = "create_date DESC"

    customer_id = fields.Many2one(
        'res.partner', string='Customer', required=True, default=lambda self: self.env.user.partner_id, domain=[('customer', '=', True)])
    review_help = fields.Selection(
        [("yes", "Helpful"), ("no", "Not Helpful")], string="Was this review helpful?", required=True)
    seller_review_id = fields.Many2one("seller.review")

    @api.multi
    def _single_user_per_product(self):
        x = self.search([('customer_id', '=', self.customer_id.id),
                         ('seller_review_id', '=', self.seller_review_id.id)])
        if len(x) > 1:
            return False
        else:
            return True

    _constraints = [
        (_single_user_per_product, _('Error ! This user have already voted for Helpful/not Helpful.'),
         ['customer_id', 'seller_review_id'])
    ]


class SellerRecommendation(models.Model):
    _name = "seller.recommendation"
    _description = "Seller Recommendation"
    _rec_name = "customer_id"

    customer_id = fields.Many2one(
        'res.partner', string='Customer', required=True, default=lambda self: self.env.user.partner_id, domain=[('customer', '=', True)])
    recommend_state = fields.Selection(
        [('yes', 'YES'), ('no', 'NO')], string="Recommend", default="no", translate=True)
    seller_id = fields.Many2one(
        "res.partner", string="Recommended Seller", required=True, domain=[('seller', '=', True)])
    state = fields.Selection(
        [('pub', 'Published'), ('unpub', 'Unpublished')], default="unpub", translate=True)

    @api.multi
    def _single_user_per_seller(self):
        x = self.search([('customer_id', '=', self.customer_id.id),
                         ('seller_id', '=', self.seller_id.id)])
        if len(x) > 1:
            return False
        else:
            return True

    _constraints = [
        (_single_user_per_seller, _('Error ! This user have already voted for recommendation.'), [
         'customer_id', 'seller_id'])
    ]

    @api.multi
    def publish_unpublish_btn(self):
        for rec in self:
            if rec.state == "pub":
                rec.state = "unpub"
            else:
                rec.state = "pub"
