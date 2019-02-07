# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Pages(models.Model):
    _name = 'megamenu.links'
    _description = 'Website megamenu links'

    link_type = fields.Selection(selection=[('product.public.category','Category'),
                                            ('event.event','Event'),
                                            ('website.page','Page'),
                                            ('product.template','Product')],
                                 string='Link Type', default='product.public.category', translate=True)
    name = fields.Char(string='Name', translate=True)
    link_category = fields.Many2one('product.public.category', string='Category Name',
                                    domain=['|',('parent_id','=',False),('parent_id.parent_id','=',False)])
    link_events = fields.Many2one('event.event', string='Event Name', domain=[('website_published','=',True)])
    link_pages = fields.Many2one('website.page', string='Page Name', domain=[('website_published','=',True)])
    link_products = fields.Many2one('product.template', string='Product Name',
                                    domain=[('website_published','=',True)])
    url = fields.Char(string='URL', default="#")
    description = fields.Char(string='Description', translate=True)
    pos_row = fields.Integer(string='Row-Position')
    pos_column = fields.Integer(string='Column-Position')
    image = fields.Binary(string='Image', store=True)
    image_name = fields.Char(string='Image Name')
    megamenu_id = fields.Many2one('megamenu.content', string='Mega Menu')

    @api.onchange('link_type')
    def setRelationSelection(self):
        self.update({'link_category': None, 'link_events': None, 'link_pages': None,
                     'link_products': None, 'url': None, 'name': None})

    @api.onchange('link_category', 'link_events', 'link_pages', 'link_products')
    def setNameUrl(self):
        if self.link_type == 'product.public.category':
            if self.link_category:
                self.update({'name': self.link_category.name,
                             'url': '/shop/category/' + str(self.link_category.id)})
            else:
                self.update({'name': None, 'url': None})
        elif self.link_type == 'event.event':
            if self.link_events:
                self.update({'name': self.link_events.name, 'url':self.link_events.website_url})
            else:
                self.update({'name': None, 'url': None})
        elif self.link_type == 'website.page':
            if self.link_pages:
                self.update({'name': self.link_pages.name, 'url':self.link_pages.url})
            else:
                self.update({'name': None, 'url': None})
        elif self.link_type == 'product.template':
            if self.link_products:
                self.update({'name': self.link_products.name,
                             'url':'/shop/product/' + str(self.link_products.id)})
            else:
                self.update({'name': None, 'url': None})
        else:
            self.update({'name': None, 'url': None})


class ContentSectionGroup(models.Model):
    _name = 'megamenu.content_section'
    _description = 'Website megamenu contents'
    
    name = fields.Char(string='Name', translate=True)
    content_section_pos = fields.Integer(string='Content Section Position')
    content_html = fields.Html(string='Content HTML', translate=True)
    megamenu_id = fields.Many2one('megamenu.content', string='Mega Menu')


class ColumnHeadline(models.Model):
    _name = 'megamenu.column_headline'
    _description = 'Website megamenu column heading'

    name = fields.Char(string='Title', required=True, translate=True)
    headline_link = fields.Char(string='Headline Link', translate=True)
    description = fields.Text(string='Description', translate=True)
    pos_column = fields.Integer(string='Column-Position')
    megamenu_id = fields.Many2one('megamenu.content', string='Mega Menu')


# class CategoryFirstLevel(models.Model):
#     _name = 'megamenu.categories_first_level'

#     name = fields.Many2one('product.public.category', string='Category Name', domain=[('parent_id','=',False)])
#     level = fields.Integer(string='Level', default=1)
#     sequence = fields.Integer(string='Sequence', default=10)
#     megamenu_id = fields.Many2one('megamenu.content', string='Mega Menu')


# class CategorySecondLevel(models.Model):
#     _name = 'megamenu.categories_second_level'

#     name = fields.Many2one('product.public.category', string='Category Name', domain=[('parent_id.parent_id','=',False)])
#     level = fields.Integer(string='Level', default=2)
#     sequence = fields.Integer(string='Sequence', default=10)
#     megamenu_id = fields.Many2one('megamenu.content', string='Mega Menu')


# class CategoryThirdLevel(models.Model):
#     _name = 'megamenu.categories_third_level'

#     name = fields.Many2one('product.public.category', string='Category Name', domain=[('parent_id.parent_id.parent_id','=',False)])
#     level = fields.Integer(string='Level', default=3)
#     sequence = fields.Integer(string='Sequence', default=10)
#     megamenu_id = fields.Many2one('megamenu.content', string='Mega Menu')

class CategoryThirdLevel(models.Model):
    _name = 'megamenu.categories_menu_lines'
    _order = 'sequence desc,id'
    _description = 'Website megamenu category links'

    name = fields.Many2one('product.public.category', string='Category Name', required=True)
    level = fields.Integer(string='Level')
    sequence = fields.Integer(string='Sequence', default=10)
    image = fields.Binary(string='Image', store=True)
    image_name = fields.Char(string='Image Name')
    megamenu_id = fields.Many2one('megamenu.content', string='Mega Menu')


class mega_menu_content(models.Model):
    _name='megamenu.content'
    _description = 'Website megamenu contents'
        
    name=fields.Char("Content Name",translate=True)
    active=fields.Boolean("Active",default=True)
    is_header=fields.Boolean("Header")
    is_footer=fields.Boolean("Footer")
    main_content_type=fields.Selection([('product_grid','Product Grid'),('product_list','Product Listing'),
                                        ('category_grid','Category Grid'),('category_list','Category Listing'),
                                        ('content','Content'),('mixed_list','Mixed Listing'),
                                        ('horiz_categ_toggle','Horizontal Category Toggle')],translate=True)
    no_of_columns=fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6')],
                                   string="Number of Columns",translate=True)
    product_ids=fields.Many2many("product.template",string="Products", domain=[('website_published','=',True)])
    product_lable_color=fields.Char("Product Label Color")
    header_content=fields.Html("Header Content",translate=True)
    footer_content=fields.Html("Footer Content",translate=True)
    category_ids=fields.Many2many("product.public.category",string="Category",
                                  domain=['|',('parent_id','=',False),('parent_id.parent_id','=',False)])
    category_lable_color=fields.Char("Category Label Color")
    menu_content=fields.Html("Content",translate=True)
    background_image = fields.Binary(name="backgroundImage", string="Background Image")
    background_image_pos = fields.Selection(selection=[('left',"Left"),("right","Right")],
                                            string="Background Image Position",
                                            default="left", translate=True)
    link_ids = fields.One2many('megamenu.links', 'megamenu_id', string='Linked Item')
    content_section_ids = fields.One2many('megamenu.content_section', 'megamenu_id', string='Content Sections')
    column_headline_ids = fields.One2many('megamenu.column_headline', 'megamenu_id', string='Column Headline')
    category_first_level = fields.One2many('megamenu.categories_menu_lines', 'megamenu_id', string='First Level Categories', domain=[('level','=',1)])
    category_second_level = fields.One2many('megamenu.categories_menu_lines', 'megamenu_id', string='Second Level Categories', domain=[('level','=',2)])
    category_third_level = fields.One2many('megamenu.categories_menu_lines', 'megamenu_id', string='Third Level Categories', domain=[('level','=',3)])

class website_menu(models.Model):
    _inherit="website.menu"
    
    is_mega_menu=fields.Boolean("Mega Menu")
    content_id=fields.Many2one("megamenu.content","Content")
    parent_id=fields.Many2one('website.menu', 'Parent Menu', index=True,
                              ondelete="cascade",domain=[('is_mega_menu','=',False)])
