# -*- coding: utf-8 -*-
import odoo
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.addons.odoo_marketplace.controllers.main import AuthSignupHome
from odoo.addons.odoo_marketplace.controllers.main import website_marketplace_dashboard


class AuthSignupHome(AuthSignupHome):
    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password', 'is_seller', 'is_delivery',
                                                      'fleet', 'state_id', 'district_id', 'city_id', 'street', 'house',
                                                      'flat', 'zip', 'mobile', 'url_handler')}
        if not values:
            raise UserError(_("The form was not properly filled in."))

        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))

        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]

        if request.lang in supported_langs:
            values['lang'] = request.lang

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
        country_russia = request.env.ref('base.ru')
        values['country_id'] = country_russia.id

        state_obj = request.env['res.country.state']
        state = state_obj.sudo().search([('code', '=', values.get('state_id'))])

        if not state:
            state = state_obj.sudo().create({
                'name': values.get('state_id'),
                'country_id': country_russia.id,
                'code': values.get('state_id'),
            })

        values['state_id'] = state.id

        district_obj = request.env['res.state.district']
        district = district_obj.sudo().search([('name', '=', values.get('district_id')), ('state_id', '=', state.id)])

        city_obj = request.env['res.city']
        city = city_obj.sudo().search([('name', '=', values.get('city_id')), ('state_id', '=', state.id)])

        if not district:
            district = district_obj.sudo().create({
                'name': values.get('district_id'),
                'state_id': state.id,
            })
        else:
            city = city_obj.sudo().search([('name', '=', values.get('city_id')), ('state_id', '=', state.id),
                                           ('district_id', '=', district.id)])
        values['district_id'] = district.id

        if not city:
            city = city_obj.sudo().create({
                'name': values.get('city_id'),
                'state_id': state.id,
                'district_id': district.id,
                'country_id': country_russia.id
            })
        values['city_id'] = city.id
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()


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
