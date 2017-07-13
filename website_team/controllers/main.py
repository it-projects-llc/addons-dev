# -*- coding: utf-8 -*-
from openerp import http
import werkzeug
from werkzeug.exceptions import NotFound

class WebsiteTeam(http.Controller):

    @http.route('/team/', auth='public', website=True)
    def index(self, **kw):
        users = http.request.env['res.users'].sudo()
        return http.request.render('website_team.team_template', {
            'users': users.search([])
        })

    @http.route('/team/<string:login>', auth='public', website=True)
    def user(self, login):

        current_user = http.request.env['res.users'].sudo().search([('username_github', '=', login)])

        if not current_user:
            current_user = http.request.env['res.users'].sudo().search([('alias_name', '=', login)])
            print current_user.username_github
            if current_user.username_github is not False and current_user.username_github != current_user.alias_name:
                return werkzeug.utils.redirect("/team/" + current_user.username_github)

        if current_user.id is False:
            raise NotFound()

        youtube_id = current_user.get_youtube_id(current_user.presentation_youtube_link)
        alias_email_full = current_user.get_alias_mail()

        return http.request.render('website_team.user_template', {
                                       'user': current_user,
                                       'youtube_id': youtube_id,
                                       'alias_email': alias_email_full,
                    })
