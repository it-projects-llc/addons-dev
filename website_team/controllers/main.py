from openerp import http
import werkzeug
from werkzeug.exceptions import NotFound


class WebsiteTeam(http.Controller):

    @http.route('/team/', auth='public', website=True)
    def index(self, **kw):
        users = http.request.env['res.users'].sudo()
        return http.request.render('website_team.team_template', {
            'users': users.search([('website_published', '=', True)], order='create_date'),
            'company': http.request.env.user.company_id,
        })

    @http.route('/team/<string:login>', auth='public', website=True)
    def user(self, login):
        User = http.request.env['res.users'].with_context(active_test=False).sudo()
        current_user = User.search([('username_github', '=', login), ('website_published', '=', True)])

        if not current_user:
            current_user = User.search([('alias_name', '=', login), ('website_published', '=', True)])
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
