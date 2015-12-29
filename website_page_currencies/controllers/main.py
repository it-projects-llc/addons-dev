# -*- coding: utf-8 -*-
from openerp import http
from openerp.addons.base import res
import werkzeug

class website_page_currencies(http.Controller): 
    @http.route('/currencies/<string:currencyline>/', auth='public', website=True)
    def index(self, currencyline, **kw):
        currencies = http.request.env['res.currency']
        currency_object = currencies.search([('name', '=', currencyline)])
        if len(currency_object) == 0:
            from werkzeug.exceptions import NotFound
            raise NotFound()
        return http.request.render('website_page_currencies.index', {
            'currencies': currencies.search([]), 'currencyline': currencies.search([('name', '=', currencyline)])
        })
    @http.route('/currencies/', auth='public', website=True)
    def redirect_index(self, **kw):
        location = '/currencies/EUR'
        return werkzeug.utils.redirect(location)
         
             
    


