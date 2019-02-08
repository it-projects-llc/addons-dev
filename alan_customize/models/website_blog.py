# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class BlogConfigure(models.Model):
    _name = 'blog.configure'
    _description = 'Blog configuration for blog snippets'    

    name= fields.Char("Blog Slider Title",traslate=True)
    blog_ids=fields.Many2many("blog.post",string="Blog Post",domain=[('website_published','=',True)])
    active=fields.Boolean("Active")
