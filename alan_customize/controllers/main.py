# -*- coding: utf-8 -*-


from odoo import fields,http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import QueryURL
from odoo.addons.website_sale.controllers import main
from odoo.addons.website.controllers.main import Website

import math
import os

main.PPG = 18
PPG=main.PPG


class Website(Website):

    @http.route('/update_scss_file', type='http', auth='public', website=True)
    def update_file(self, **kw):
        if kw['write_str']:
            module_str = '/'.join((os.path.realpath(__file__)).split('/')[:-2])
            f = open(module_str + '/static/src/scss/options/colors/website_'+str(request.website.id)+'_color_picker.scss', 'w+')
            f.write(kw['write_str'])
            f.close()
        return None
        
    @http.route()
    def theme_customize(self, enable, disable, get_bundle=True):
        """ enable or Disable lists of ``xml_id`` of the inherit templates """
        def set_active(ids, active):
            if ids:
                real_ids = self.get_view_ids(ids)
                request.env['ir.ui.view'].browse(real_ids).write({'active': active})

        set_active(disable, False)
        set_active(enable, True)
        template = ''
        context = dict(request.context)
        if enable:
            for i in enable:
                if i.startswith('theme_alan.header_layout_'):
                     if  not i.endswith('_css'):
                         templ = i+'_css'
                         views = request.env['ir.ui.view'].search([('key','ilike','theme_alan.header_layout_')])
                         for v in views:
                            if v.key.endswith('_css'):
                                set_active([v.key], False)
                         set_active([templ], True)

                if i.startswith('theme_alan.footer_layout_'):
                     if  not i.endswith('_css'):
                         templ = i+'_css'
                         views = request.env['ir.ui.view'].search([('key','ilike','theme_alan.footer_layout_')])
                         for v in views:
                            if v.key.endswith('_css'):
                                set_active([v.key], False)
                         set_active([templ], True)

        if get_bundle:
            context = dict(request.context)
            return request.env["ir.qweb"]._get_asset('web.assets_frontend', options=context)

        return True


class WebsiteSale(WebsiteSale):
    @http.route(
        ['/page/product_brands'],
        type='http',
        auth='public',
        website=True)
    def product_brands(self, **post):
        cr, context, pool = (request.cr,
                             request.context,
                             request.registry)
        b_obj = request.env['product.brand']
        domain = []
        if post.get('search'):
            domain += [('name', 'ilike', post.get('search'))]
        brand_ids = b_obj.search(domain)

        keep = QueryURL('/page/product_brands', brand_id=[])
        values = {'brand_rec': brand_ids,
                  'keep': keep}
        if post.get('search'):
            values.update({'search': post.get('search')})
        return request.render(
            'alan_customize.product_brands',
            values)

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        add_more = False
        website = request.website
        quantities_per_page = None
        if website.shop_product_loader == 'infinite_loader':
            add_more = True
        quantities_per_page = request.env['product.qty_per_page'].search([], order='sequence')
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = quantities_per_page[0].name if quantities_per_page else PPG
            res = super(WebsiteSale, self).shop(page, category, search, ppg, **post)
            if 'ppg' in post:
                post["ppg"] = ppg
        else:
            ppg = quantities_per_page[0].name if quantities_per_page else PPG
            res = super(WebsiteSale, self).shop(page, category, search, ppg, **post)
        product_ids = request.env['product.template'].search(['&', ('sale_ok', '=', True), ('active', '=', True)])
        request._cr.execute('SELECT min(list_price), max(list_price) FROM product_template WHERE id IN %s', [tuple(product_ids.ids)])
        min_max_vals = request.cr.fetchall()
        min_val = min_max_vals[0][0] or 0
        if int(min_val) == 0:
            min_val = 1
        max_val = min_max_vals[0][1] or 1
        
        custom_min_val = custom_max_val = 0
        if post.get('min_val') and post.get('max_val'):
            custom_min_val = float(post.get('min_val'))
            custom_max_val = float(post.get('max_val'))
            post.update({'attrib_price': '%s-%s' % (custom_min_val, custom_max_val)})
        else:
            post.update({'attrib_price': '%s-%s' % (min_val, max_val)})
        
        res.qcontext.update({
            'ppg': ppg,
            'quantities_per_page': quantities_per_page,
            'add_more': add_more,
            'min_val': min_val,
            'max_val': max_val,
            'custom_min_val': custom_min_val,
            'custom_max_val': custom_max_val,
            'floor': math.floor,
            'ceil': math.ceil
        })
        
        if post.get('brand') or post.get('product_collection') or (post.get('min_val') and post.get('max_val')) :
            attrib_list = request.httprequest.args.getlist('attrib')
            attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
            attributes_ids = {v[0] for v in attrib_values}
            attrib_set = {v[1] for v in attrib_values}

            domain = self._get_search_domain(search, category, attrib_values)

            if post.get('brand'):
                product_designer_obj = request.env['product.brand']
                brand_ids = product_designer_obj.search([('id', '=', int(post.get('brand')))])
                if brand_ids:
                    domain += [('product_brand_id', 'in', brand_ids.ids)]

            if post.get('product_collection'):
                prod_collection_rec = request.env['multitab.configure'].search([('id','=',int(post.get('product_collection')))])
                if prod_collection_rec:
                    prod_id_list = list({each_p.product_id.id for each_p in prod_collection_rec.product_ids})
                    domain += [('id','in',prod_id_list)]
            if post.get('min_val') and post.get('max_val'):
                domain += [('list_price','>=',float(post.get('min_val'))),('list_price','<=',float(post.get('max_val')))]
            keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

            pricelist_context = dict(request.env.context)

            if not pricelist_context.get('pricelist'):
                pricelist = request.website.get_current_pricelist()
                pricelist_context['pricelist'] = pricelist.id
            else:
                pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

            request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

            url = "/shop"
            if search:
                post["search"] = search
            if category:
                category = request.env['product.public.category'].browse(int(category))
                url = "/shop/category/%s" % slug(category)
            if attrib_list:
                post['attrib'] = attrib_list

            categs = request.env['product.public.category'].search([('parent_id', '=', False)])
            Product = request.env['product.template']

            parent_category_ids = []
            if category:
                parent_category_ids = [category.id]
                current_category = category
                while current_category.parent_id:
                    parent_category_ids.append(current_category.parent_id.id)
                    current_category = current_category.parent_id

            product_count = Product.search_count(domain)

            pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
            products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

            ProductAttribute = request.env['product.attribute']

            if products:
                selected_products = Product.search(domain, limit=False)
                attributes = ProductAttribute.search([('attribute_line_ids.product_tmpl_id', 'in', selected_products.ids)])
            else:
                attributes = ProductAttribute.browse(attributes_ids)

            from_currency = request.env.user.company_id.currency_id
            to_currency = pricelist.currency_id
            compute_currency, pricelist_context, pricelist = self._get_compute_currency_and_context()
            res.qcontext.update({
                'search': search,
                'category': category,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'pager': pager,
                'products': products,
                'search_count': product_count,
                'bins': TableCompute().process(products, ppg),
                'categories': categs,
                'attributes': attributes,
                'compute_currency': compute_currency,
                'keep': keep,
                'parent_category_ids': parent_category_ids,
                'product_collection': post.get('product_collection'),
            })
        return res

    @http.route(['/shop/cart/clean_cart'], type='json', auth="public", website=True)
    def clean_cart(self, type_id=None):
        order = request.website.sale_get_order()
        request.website.sale_reset()
        if order:
            order.sudo().unlink();
        return {}

    @http.route(['/shop/product/update_cart_popup'], type='http', auth="public", website=True)
    def update_cart_popup(self):
        order = request.website.sale_get_order()
        return request.render("alan_customize.product_cart", {'website':request.website})

    @http.route(['/shop/product/whishlists/move_to_cart'], type='json', auth="public", website=True)
    def move_to_cart(self, line_id=None):
        if line_id:
            product_data=request.env['product.wishlist'].browse(line_id)
            request.website.sale_get_order(force_create=1)._cart_update(product_id=int(product_data.product_id.id), add_qty=float(1), set_qty=float(1))
        return True 
    
    @http.route(['/shop/product/whishlists/add_all_to_cart'], type='json', auth="public", website=True)
    def add_all_to_cart(self, line_id=None): 
        cr,uid=request.cr,request.uid 
        line_ids=request.env['product.wishlist'].search([('user_id','=',uid)])
        for data in line_ids:
            request.website.sale_get_order(force_create=1)._cart_update(product_id=int(data.product_id.id), add_qty=float(1), set_qty=float(1))
        return True 

      

    @http.route('/update_my_wishlist', type="http", auth="public", website=True)
    def qv_update_my_wishlist(self, **kw):
        if kw['prod_id']:
            self.add_to_wishlist(product_id=int(kw['prod_id']))
        return

    @http.route('/get_qv_prod_variant', type="json", auth="public", website=True)
    def get_qv_product_variant(self, **kw):
        ret = {}
        attribute_values_array = kw['attribute_values_array']
        prod_template = http.request.env['product.template'].search([("id",'=',int(kw['prod_template_id']))])
        if prod_template and len(prod_template) == 1:
            data = []
            for each_variant in prod_template[0].product_variant_ids:
                db_attribute_values_array = []
                for each_attrb_value in each_variant.attribute_value_ids:
                    num_of_values = http.request.env['product.attribute.value'].search([('attribute_id','=',each_attrb_value.attribute_id.id)])
                    if num_of_values and len(num_of_values) > 1:
                        db_attribute_values_array.append(each_attrb_value.id)
                if (len(set(db_attribute_values_array).intersection(set(attribute_values_array))) == len(attribute_values_array)) and (len(db_attribute_values_array) == len(attribute_values_array)):
                    data.append(each_variant)
            if len(data) == 1:
                ret['product_product_id'] = data[0].id
        return ret

    @http.route(['/shop/load_next_products'], type="http", auth="public", website=True)
    def load_next_products(self, category='', loaded_products=0, search='', ppg=0, **post):
        if ppg:
            request.cr.execute('select min(list_price),max(list_price) from product_template where sale_ok=True and active=True and is_published=True')
            min_max_vals = request.cr.fetchall()
            min_val = min_max_vals[0][0] or 0
            if int(min_val) == 0:
                min_val = 1
            max_val = min_max_vals[0][1] or 1
            
            custom_min_val = custom_max_val = 0
            if post.get('min_val') and post.get('max_val'):
                custom_min_val = float(post.get('min_val'))
                custom_max_val = float(post.get('max_val'))
                post.update({'attrib_price':'%s-%s'%(custom_min_val,custom_max_val)})
            else:
                post.update({'attrib_price':'%s-%s'%(min_val,max_val)})

            attrib_list = request.httprequest.args.getlist('attrib[]')
            attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
            attributes_ids = {v[0] for v in attrib_values}
            attrib_set = {v[1] for v in attrib_values}
            domain = self._get_search_domain(search, category, attrib_values)
            if post.get('brand'):
                product_designer_obj = request.env['product.brand']
                brand_ids = product_designer_obj.search([('id', '=', int(post.get('brand')))])
                if brand_ids:
                    domain += [('product_brand_id', 'in', brand_ids.ids)]
            if post.get('min_val') and post.get('max_val'):
                domain += [('list_price','>=',float(post.get('min_val'))),('list_price','<=',float(post.get('max_val')))]
            if post.get('product_collection'):
                prod_collection_rec = request.env['multitab.configure'].search([('id','=',int(post.get('product_collection')))])
                if prod_collection_rec:
                    prod_id_list = list({each_p.product_id.id for each_p in prod_collection_rec.product_ids})
                    domain += [('id','in',prod_id_list)]
            keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))
            pricelist_context = dict(request.env.context)
            if not pricelist_context.get('pricelist'):
                pricelist = request.website.get_current_pricelist()
                pricelist_context['pricelist'] = pricelist.id
            else:
                pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

            request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)
            url = "/shop"
            if search:
                post["search"] = search
            if category:
                category = request.env['product.public.category'].browse(int(category))
                url = "/shop/category/%s" % slug(category)
            if attrib_list:
                post['attrib'] = attrib_list
            categs = request.env['product.public.category'].search([('parent_id', '=', False)])
            Product = request.env['product.template']
            parent_category_ids = []
            if category:
                parent_category_ids = [category.id]
                current_category = category
                while current_category.parent_id:
                    parent_category_ids.append(current_category.parent_id.id)
                    current_category = current_category.parent_id

            product_count = Product.search_count(domain)
            products = Product.search(domain, limit=int(ppg), offset=int(loaded_products), order=self._get_search_order(post))
            ProductAttribute = request.env['product.attribute']
            if products:
                attributes = ProductAttribute.search([('attribute_line_ids.product_tmpl_id', 'in', products.ids)])
            else:
                attributes = ProductAttribute.browse(attributes_ids)

            from_currency = request.env.user.company_id.currency_id
            to_currency = pricelist.currency_id
            compute_currency, pricelist_context, pricelist = self._get_compute_currency_and_context()
            values = {
                'compute_currency': compute_currency,
                'add_more': True if request.website.shop_product_loader == 'infinite_loader' else False,
                'products': products,
                'keep': keep,
            }
            return request.render('alan_customize.newly_loaded_products', values)
        else:
            return None

    @http.route()
    def cart(self, access_token=None, revive='', **post):
        res = super(WebsiteSale, self).cart(access_token, revive, **post)
        if post.get('type')=='cart_lines_popup':
            return request.render('alan_customize.cart_lines_popup_content', res.qcontext)
        else:
            return res

    @http.route('/check_magnifier_status', type='json', auth='public', website=True)
    def check_magnifier_status(self, **kw):
        # status = False
        view_rec = request.env['ir.ui.view'].search([('key','=like','alan_customize.product_picture_magnify')]) #('id','=',1307),('key','=like','alan_customize.product_picture_magnify')
        return {'status': view_rec.active if view_rec else False}


