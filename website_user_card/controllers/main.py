# -*- coding: utf-8 -*-
from openerp import http
import werkzeug

class website_user_card(http.Controller):

    @http.route('/page/user/', auth='public', website=True)
    def redirect_index(self, **kw):
        location = '/page/users/'
        return werkzeug.utils.redirect(location)

    @http.route('/page/users/', auth='public', website=True)
    def index(self, **kw):
        users = http.request.env['res.users'].sudo()
        return http.request.render('website_user_card.uindex', {
            'users': users.search([])
        })

    @http.route('/page/user/<string:user_login>', auth='public', website=True)
    def user(self, user_login):

        users = http.request.env['res.users'].sudo()
        # partners = http.request.env['res.users.partner_id'].sudo()

        # user1 = users.search([('login', '=', user_login)])
        # user_id = partners.search([('partner_id', '=', user1.partner_id)])
        if len(user_login) == 0:
            location = '/page/users/'
            return werkzeug.utils.redirect(location)
        else:
            return http.request.render('website_user_card.test_user', {
                'user': users.search([('login', '=', user_login)]),
                # 'partner': partners.search([('login', '=', user_login)])
            })
