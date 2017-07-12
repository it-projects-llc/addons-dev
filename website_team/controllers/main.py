# -*- coding: utf-8 -*-
from openerp import http
import werkzeug


class WebsiteTeam(http.Controller):

    @http.route('/team/', auth='public', website=True)
    def index(self, **kw):
        users = http.request.env['res.users'].sudo()
        return http.request.render('website_team.team_template', {
            'users': users.search([])
        })

    @http.route('/team/<string:user_gh>', auth='public', website=True)
    def user(self, user_gh):

        current_user = http.request.env['res.users'].sudo().search([('username_github', '=', user_gh)])
        youtube_id = current_user.get_youtube_id(current_user.presentation_youtube_link)
        alias_email_full = current_user.alias_name + "@" + current_user.alias_domain

        if len(user_gh) == 0:
            location = '/team/'
            return werkzeug.utils.redirect(location)
        else:
            return http.request.render('website_team.test_user', {
                'user': current_user,
                'youtube_link': youtube_id,
                'alias_email': alias_email_full
            })
