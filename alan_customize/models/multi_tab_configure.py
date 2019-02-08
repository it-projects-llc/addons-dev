# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class Multitab_configure(models.Model):
    _name = 'multitab.configure'
    _description = 'Tab configuration for product snippets'
    
    name = fields.Char("Group Name")
    product_ids = fields.One2many("tab.products","tab_id",string="Products")
    active = fields.Boolean("Active")
    image = fields.Binary(string="Image", store=True)
    image_filename = fields.Char(string='Image Filename')


class Tab_collection_product(models.Model):
    _name= "tab.products"
    _order = "sequence desc,id"
    _description = 'Product collection for tabs'
    
    product_id = fields.Many2one("product.template",string="Products",
                                 domain=[('website_published','=',True)])
    sequence = fields.Integer(string="Sequence")
    tab_id = fields.Many2one("multitab.configure",string ="Tab Id")


class Collection_configure(models.Model):
    _name = 'collection.configure'
    _description = 'Tab collections'
    
    name = fields.Char("Title")
    tab_collection_ids = fields.Many2many('multitab.configure',string="Select Collection")
    active = fields.Boolean("Active")


# class CtProductTabs(models.Model):
#     _name = 'ct.product.tabs'
#     _order = "sequence, name"
    
#     active = fields.Boolean(default=1)
#     sequence = fields.Integer(string="Sequence")
#     name = fields.Char(required=1,translate= True, string="Name")
#     content = fields.Html(required=1,translate= True)
#     tab_product_id  = fields.Many2one(comodel_name='product.template',string='Product')


# class Product(models.Model):
#     _inherit = 'product.template'

#     product_ct_tab_ids = fields.One2many(
#         comodel_name='ct.product.tabs',
#         inverse_name='tab_product_id',
#         string='Product Tabs'
#     )
