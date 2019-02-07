# -*- coding: utf-8 -*-

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from odoo import SUPERUSER_ID
from odoo import fields,http


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/get_products_content'], type='http', auth='public', website=True)
    def get_products_content(self, **post):
        pricelist_context = dict(request.env.context)
        pricelist = False
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])
        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)
        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency._convert(
                price, to_currency, request.env.user.company_id, fields.Date.today())  
        if post.get('tab_id'):
            tab_data = request.env['multitab.configure'].browse(int(post.get('tab_id')))
            return request.render("alan_customize.product_slider_content", {'product_collection':tab_data,'compute_currency': compute_currency,'limit' : post.get('limit') or 0,'full_width':post.get('full_width')})
        return ''

    @http.route(['/shop/get_product_brand_slider'], type='http', auth='public', website=True)
    def get_product_brand_slider(self, **post):
        value = {'header': False,'brands':False}
        if post.get('label'):
            value['header'] = post.get('label')
        if post.get('brand-count'):
            brand_ids=request.env['product.brand'].search([('visible_slider','=',True)])
            if brand_ids:
                value.update({'brands':brand_ids})
        return request.render("alan_customize.brand_slider_content", value)

    @http.route(['/shop/get_latest_p'], type='http', auth='public', website=True)
    def get_product_latest_p(self,tab_id=0, **post):
        value = {'header': False,'brands':False,'full_width':post.get('full_width')}

        from_currency = request.env.user.company_id.currency_id
        pricelist_context = dict(request.env.context)
        pricelist = False
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency._convert(
                price, to_currency, request.env.user.company_id, fields.Date.today())
        if tab_id:
            tab = request.env['multitab.configure'].browse(int(tab_id))
            if tab:
                value.update({'tab_obj': tab,'compute_currency': compute_currency})
            return request.render("alan_customize.latest_p_content", value)

    @http.route(['/shop/get_multi_tab_content'], type='http', auth='public', website=True)
    def get_multi_tab_content(self, **post):
        pricelist_context = dict(request.env.context)
        pricelist = False
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])
        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)
        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency._convert(
                price, to_currency, request.env.user.company_id, fields.Date.today())
        value = {'obj': False,'compute_currency': compute_currency}
        if post.get('label'):
            value['header'] = post.get('label')
        if post.get('collection_id'):
            collection_data=request.env['collection.configure'].browse(int(post.get('collection_id')))
            value.update({'obj':collection_data})
            return request.render("alan_customize.s_collection_configure", value)

        return ""

    @http.route(['/shop/multi_tab_product_snippet'], type='http', auth='public', website=True)
    def multi_tab_product_snippet(self, **post):
        pricelist_context = dict(request.env.context)
        pricelist = False
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])
        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)
        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency._convert(
                price, to_currency, request.env.user.company_id, fields.Date.today())
        value = {'product_obj': False,'compute_currency': compute_currency}
        if post.get('label'):
            value['header'] = post.get('label')
        if post.get('collection_id'):
            collection_data=request.env['collection.configure'].browse(int(post.get('collection_id')))
            value.update({'product_obj':collection_data})

        return request.render("alan_customize.product_tab_content", value)

    @http.route('/shop/get_product_collection', type='http', auth='public', website=True)
    def product_slider_collection(self, **post):
        value = {}
        from_currency = request.env.user.company_id.currency_id
        pricelist_context = dict(request.env.context)
        pricelist = False
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency._convert(
                price, to_currency, request.env.user.company_id, fields.Date.today())
        if post.get('collection_id'):
            collection = request.env['multitab.configure'].browse(int(post.get('collection_id')))
            if collection:
                value.update({'product_collection': collection,'compute_currency': compute_currency})
            return request.render("alan_customize.product_slider_2_content", value)

    @http.route('/get_product_img_gallery', type='http', auth='public', website=True)
    def get_product_img_gallery(self, **post):
        value = {}
        if 'product_id' in post and post.get('product_id'):
            p_var_rec = request.env['product.product'].search([('id','=',int(post.get('product_id')))])
            value['variant_img'] = p_var_rec if len(p_var_rec.product_tmpl_id.product_variant_ids) > 1 else False
            value['product'] = p_var_rec.product_tmpl_id

            return request.render('alan_customize.product_image_gallery_content', value)
        return ''

    @http.route('/shop/get_product_snippet_content', type='http', auth='public', website=True)
    def get_product_snippet_content(self, **post):
        if post.get('snippet_type') and post.get('collection_id') and post.get('snippet_layout'):
            if post.get('snippet_type') == 'single':
                if post.get('snippet_layout') == 'slider':
                    post['tab_id'] = post.get('collection_id')
                    return self.get_products_content(**post)
                elif post.get('snippet_layout') == 'fw_slider':
                    post['tab_id'] = post.get('collection_id')
                    post['full_width'] = True
                    return self.get_products_content(**post)
                elif post.get('snippet_layout') == 'slider_img_left':
                    return self.product_slider_collection(**post)
                elif post.get('snippet_layout') == 'grid':
                    post['tab_id'] = post.get('collection_id')
                    return self.get_product_latest_p(**post)
                elif post.get('snippet_layout') == 'fw_grid':
                    post['tab_id'] = post.get('collection_id')
                    post['full_width'] = True
                    return self.get_product_latest_p(**post)
                else:
                    return ''
            elif post.get('snippet_type') == 'multi':
                if post.get('snippet_layout') == 'horiz_tab':
                    return self.get_multi_tab_content(**post)
                elif post.get('snippet_layout') == 'vertic_tab':
                    return self.multi_tab_product_snippet(**post)
                else:
                    return ''
            else:
                return ''
        return ''
