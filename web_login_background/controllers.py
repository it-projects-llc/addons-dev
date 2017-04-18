# -*- coding: utf-8 -*-

from openerp import http
from openerp.addons.web.controllers.main import Home
from openerp.http import request
from openerp.addons.auth_signup.controllers.main import AuthSignupHome


class Background(Home):

    @http.route('/web/login', type='http', auth="public")
    def web_login(self, redirect=None, **kw):
        picture_url = request.env['ir.attachment'].get_background_pic()
        if picture_url:
            request.params['picture_url'] = picture_url

        return super(Background, self).web_login(**kw)


class BackgroundSignup(AuthSignupHome):

    @http.route('/web/signup', type='http', auth="public")
    def web_auth_signup(self, redirect=None, **kw):
        picture_url = request.env['ir.attachment'].get_background_pic()
        if picture_url:
            request.params['picture_url'] = picture_url

        return super(BackgroundSignup, self).web_auth_signup(**kw)
