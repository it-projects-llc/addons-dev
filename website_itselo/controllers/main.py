# -*- coding: utf-8 -*-
import odoo
from odoo import http
from odoo.http import request
from odoo.addons.odoo_marketplace.controllers.main import AuthSignupHome
from odoo.addons.odoo_marketplace.controllers.main import website_marketplace_dashboard


class AuthSignupHome(AuthSignupHome):

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in (
        'login', 'name', 'password', 'is_seller', 'is_delivery', 'fleet', 'state_id', 'district_id', 'city_id',
        'street', 'house', 'flat', 'zip', 'mobile', 'url_handler')}
        # Доставщик
        if values.get('is_delivery'):
            Fleet = request.env['fleet.vehicle']
            mod = request.env['fleet.vehicle.model'].sudo().search([('name', '=', 'default')])
            if mod:
                auto = Fleet.sudo().create({
                    'model_id': mod.id,
                    'license_plate': values.get('fleet'),
                })
            else:
                brand = request.env['fleet.vehicle.model.brand'].sudo().create({'name': 'default'})
                model = request.env['fleet.vehicle.model'].sudo().create({'name': 'default', 'brand_id': brand.id})
                auto = Fleet.sudo().create({
                    'model_id': model.id,
                    'license_plate': values.get('fleet'),
                })
            values['fleet_id'] = auto.id

        # Адрес
        state = values.get('state_id')
        district = values.get('district_id')
        city = values.get('city_id')

        state_id = request.env['res.country.state']
        city_id = request.env['res.city']
        values['country_id'] = 190
        search_state = state_id.sudo().search([('code', '=', state)])
        search_city = city_id.sudo().search([('name', '=', city), ('state_id', '=', search_state.id)]).id
        # State
        if search_state:
            values['state_id'] = search_state.id
        else:
            s_id = request.env['res.country.state'].sudo().create({
                'name': state,
                'country_id': 190,
                'code': state,
            })
            values['state_id'] = s_id.id

        # City
        if search_city:
            values['city_id'] = search_city
        else:
            c_id = request.env['res.city'].sudo().create({
                'name': city,
                'state_id': search_state.id or s_id.id,
            })
            values['city_id'] = c_id.id
        super(AuthSignupHome, self).do_signup(qcontext)


class WebsiteMarketplaceDashboard(website_marketplace_dashboard):
    @http.route('/my/marketplace/become_seller', type='http', auth="public", website=True)
    def become_seller(self, **post):
        partner = request.env.user.partner_id
        if request.env.user.id == request.website.user_id.id:
            return request.redirect('/seller')
        if partner.user_id:
            sales_rep = partner.user_id
        else:
            sales_rep = False
        values = {
            'sales_rep': sales_rep,
            'company': request.website.company_id,
            'user': request.env.user,
            'is_seller': True,
        }
        return request.render('odoo_marketplace.convert_user_into_seller', values)
