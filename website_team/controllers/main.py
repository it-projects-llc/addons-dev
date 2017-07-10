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

        users = http.request.env['res.users'].sudo()
        # alias = http.request.env['mail.alias'].sudo()
        # users_name = users.search([('username_github', '=', user_gh)])
        # aliasq = alias.search([('alias_user_id', '=', users_name.id)])
        #
        # print "++++++++++++++++++++++++++++++++++++++"
        # print users.search([('username_github', '=', user_gh)])
        # print aliasq #.alias_name
        # for r in aliasq:
        #     print r.alias_name
        # print "++++++++++++++++++++++++++++++++++++++"

        if len(user_gh) == 0:
            location = '/team/'
            return werkzeug.utils.redirect(location)
        else:
            return http.request.render('website_team.test_user', {
                'user': users.search([('username_github', '=', user_gh)]),
                # 'alias': aliasq
            })
