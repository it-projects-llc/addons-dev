# -*- coding: utf-8 -*-
# Part of BiztechCS. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models


class ProductCategorySlider(models.Model):
    _name = 'product.category.slider.config'

    name = fields.Char(string="Slider name", default='Trending', required=True, translate=True,
                       help="Slider title to be displayed on website like Best products, Latest and etc...")
    active = fields.Boolean(string="Active", default=True)
    no_of_counts = fields.Selection([('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')], string="Counts",
                                    default='4', required=True,
                                    help="No of products to be displayed in slider.")
    prod_cat_type = fields.Selection([('product', 'Product'), ('category', 'Category')],
                                     string="Type of slider", default='product', required=True,
                                     help="Select product or category for whom you want to show a slider.")
    auto_rotate = fields.Boolean(string='Auto Rotate Slider', default=True)
    sliding_speed = fields.Integer(string="Slider sliding speed", default='5000',
                                   help='Sliding speed of a slider can be set from here and it will be in milliseconds.')
    collections_product = fields.Many2many('product.template', 'king_pro_product_slider_rel', 'slider_id',
                                           'prod_id', string="Collections of product")
    collections_category = fields.Many2many('product.public.category', 'king_pro_category_slider_rel',
                                            'slider_id', 'cat_id', string="Collections of category")


class BlogSlider(models.Model):

    _name = 'blog.slider.config'

    name = fields.Char(string="Slider name", default='Blogs', translate=True,
                       help="Slider title to be displayed on website like Our Blogs, Latest Blog Post and etc...",
                       required=True)
    active = fields.Boolean(string="Active", default=True)
    no_of_counts = fields.Selection([('1', '1'), ('2', '2'), ('3', '3')], string="Counts",
                                    default='3', help="No of blogs to be displayed in slider.", required=True)
    auto_rotate = fields.Boolean(string='Auto Rotate Slider', default=True)
    sliding_speed = fields.Integer(string="Slider sliding speed", default='5000',
                                   help='Sliding speed of a slider can be set from here and it will be in milliseconds.')
    collections_blog_post = fields.Many2many('blog.post', 'blogpost_slider_rel', 'slider_id',
                                             'post_id', string="Collections of blog posts", required=True)


class MultiSlider(models.Model):
    _name = 'multi.slider.config'

    name = fields.Char(string="Slider name", default='Trending',
                       required=True, translate=True,
                       help="Slider title to be displayed on website like Best products, Latest and etc...")
    active = fields.Boolean(string="Active", default=True)

    auto_rotate = fields.Boolean(string='Auto Rotate Slider', default=True)
    sliding_speed = fields.Integer(string="Slider sliding speed", default='5000',
                                   help='Sliding speed of a slider can be set from here and it will be in milliseconds.')

    no_of_collection = fields.Selection([('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                        string="No. of collections to show", default='2',
                                        required=True,
                                        help="No of collections to be displayed on slider.")

    label_collection_1 = fields.Char(string="1st collection name", default='First collection',
                                     required=True, translate=True,
                                     help="Collection label to be displayed in website like Men, Women, Kids, etc...")
    collection_1_ids = fields.Many2many('product.template', 'product_slider_collection_1_rel', 'slider_id',
                                        'prod_id',
                                        required=True,
                                        string="1st product collection")

    label_collection_2 = fields.Char(string="2nd collection name", default='Second collection',
                                     required=True, translate=True,
                                     help="Collection label to be displayed in website like Men, Women, Kids, etc...")
    collection_2_ids = fields.Many2many('product.template', 'product_slider_collection_2_rel', 'slider_id',
                                        'prod_id',
                                        required=True,
                                        string="2nd product collection")

    label_collection_3 = fields.Char(string="3rd collection name", default='Third collection', translate=True,
                                     # required=True,
                                     help="Collection label to be displayed in website like Men, Women, Kids, etc...")
    collection_3_ids = fields.Many2many('product.template', 'product_slider_collection_3_rel', 'slider_id',
                                        'prod_id',
                                        # required=True,
                                        string="3rd product collection")

    label_collection_4 = fields.Char(string="4th collection name", default='Fourth collection', translate=True,
                                     # required=True,
                                     help="Collection label to be displayed in website like Men, Women, Kids, etc...")
    collection_4_ids = fields.Many2many('product.template', 'product_slider_collection_4_rel', 'slider_id',
                                        'prod_id',
                                        # required=True,
                                        string="4th product collection")

    label_collection_5 = fields.Char(string="5th collection name", default='Fifth collection', translate=True,
                                     # required=True,
                                     help="Collection label to be displayed in website like Men, Women, Kids, etc...")
    collection_5_ids = fields.Many2many('product.template', 'product_slider_collection_5_rel', 'slider_id',
                                        'prod_id',
                                        # required=True,
                                        string="5th product collection")
