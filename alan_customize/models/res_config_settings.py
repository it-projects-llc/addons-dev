# -*- coding: utf-8 -*-

from odoo import api, fields, models
import os

class Website(models.Model):
    """Adds the fields for breadcum."""

    _inherit = 'website'

    bread_cum_image = fields.Binary(string="Breadcrumb Image")
    breadcrumb_color = fields.Char('Backgroud Color #', default='black',help="For ex. #000ff;")
    breadcrumb_text_color = fields.Char('Text Color #', default='white',help="For ex. #000ff;")
    is_breadcum = fields.Boolean(string="Do you want to disable Breadcrumb?")
    breadcrumb_height = fields.Char('Padding', default='50px',help="For ex. 50px;")
    breadcum_background_image = fields.Boolean(string="Remove Breadcrumb background image?")
    shop_product_loader = fields.Selection(selection=[('infinite_loader','Infinite Loader'),('pagination','Pagination')], string='Shop Product Loader', default='infinite_loader', translate=True)
    

    def get_colors_scss(self):
        data=[]
        scss = '/static/src/scss/options/colors/color_picker.scss'
        if self.id:
            scss ='/static/src/scss/options/colors/website_'+str(self.id)+'_color_picker.scss'
        module_str = '/'.join((os.path.realpath(__file__)).split('/')[:-2])
        try:
            f = open(module_str + scss, 'r')
            f.close()
            return '/alan_customize'+scss
        except:
            return '/alan_customize/static/src/scss/options/colors/color_picker.scss'
            
    @api.model
    def get_category_breadcum(self,category):
        data=[]
        parent_categ=False
        if category:
            categ_data=self.env['product.public.category'].search([('id','=',int(category))])
            data.append(categ_data)
            parent_categ=categ_data
            if categ_data and categ_data.parent_id:
                parent_categ=categ_data.parent_id
                data.append(parent_categ)
                while parent_categ.parent_id:
                    parent_categ=parent_categ.parent_id
                    data.append(parent_categ) 
            data.reverse()
        return data

    @api.model
    def new_page(self, name=False, add_menu=False, template='website.default_page', ispage=True, namespace=None):
        res = super(Website,self).new_page(name,add_menu,template,ispage=True,namespace=namespace)
        if  ispage:  
            arch = "<?xml version='1.0'?><t t-name='website."+str(name)+"'><t t-call='website.layout'> \
                    <div id='wrap' class='oe_structure oe_empty'>"

            arch=arch+'<t t-if="not website.is_breadcum">'

            arch =arch+'<t t-if="website.breadcum_background_image">'\
                '<nav class="is-breadcrumb shop-breadcrumb" role="navigation" aria-label="breadcrumbs" t-attf-style="background:none;background-color:#{website.breadcrumb_color};padding:#{website.breadcrumb_height};">'\
                      '<div class="container">'\
                        '<h1><span t-attf-style="color:#{website.breadcrumb_text_color}">'+str(name)+'</span></h1>'\
                        '<ul class="breadcrumb">'\
                            '<li><a href="/page/homepage" t-attf-style="color:#{website.breadcrumb_text_color}">Home</a></li>'\
                            '<li class="active"><span t-attf-style="color:#{website.breadcrumb_text_color}">'+str(name)+'</span></li>'\
                        '</ul>'\
                      '</div>'\
                '</nav>'\
                '</t>'
            arch=arch+'<t t-if="not website.breadcum_background_image">'\
                '<t t-set="bread_cum" t-value="website.image_url(website,'+repr('bread_cum_image')+')"/>'\
                '<nav class="is-breadcrumb shop-breadcrumb" role="navigation" aria-label="breadcrumbs" t-attf-style="background-image:url(#{bread_cum}#);padding:#{website.breadcrumb_height};">'\
                    '<div class="container">'\
                        '<h1><span t-attf-style="color:#{website.breadcrumb_text_color}">'+str(name)+'</span></h1>'\
                        '<ul class="breadcrumb">'\
                            '<li><a href="/page/homepage" t-attf-style="color:#{website.breadcrumb_text_color}">Home</a></li>'\
                            '<li class="active"><span t-attf-style="color:#{website.breadcrumb_text_color}">'+str(name)+'</span></li>'\
                        '</ul>'\
                      '</div>'\
                '</nav>'\
            '</t>'
            arch =arch+'</t>'
            arch = arch+'</div><div class="oe_structure"/></t></t>'
            view_id = res['view_id']
            view = self.env['ir.ui.view'].browse(int(view_id))
            view.write({'arch':arch})
        return res


class WebsiteConfigSettings(models.TransientModel):
    """Settings for the Terms and Condition."""

    _inherit = 'res.config.settings'

    bread_cum_image = fields.Binary(
        related='website_id.bread_cum_image',
        string='Breadcrumb Image',readonly=False
    )
    is_breadcum = fields.Boolean(string="Do you want to disable Breadcrumb?", related='website_id.is_breadcum',readonly=False)
    breadcrumb_height = fields.Char('Padding',related='website_id.breadcrumb_height',help="For ex. 50px;",readonly=False)
    breadcum_background_image = fields.Boolean(string="Remove Breadcrumb background image?" ,related='website_id.breadcum_background_image',readonly=False)
    breadcrumb_color = fields.Char('Backgroud Color #', related='website_id.breadcrumb_color',readonly=False)
    breadcrumb_text_color = fields.Char('Text Color #', related='website_id.breadcrumb_text_color',readonly=False)
    shop_product_loader = fields.Selection(selection=[('infinite_loader','Infinite Loader'),('pagination','Pagination')], related='website_id.shop_product_loader', default='infinite_loader', translate=True,readonly=False)

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    hover_image = fields.Binary("Hover Image")
