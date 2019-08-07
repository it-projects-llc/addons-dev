from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserError
import re


class Users(models.Model):
    _inherit = ['res.users']

    username_github = fields.Char(default=None, string="Github user", help="User GitHub name")
    url_upwork = fields.Char(default=None, string="Upwork link", help="User upwork link")
    username_twitter = fields.Char(string="Twitter link", help="User twitter link")
    presentation_youtube_link = fields.Char(string='YouTube representation video link',
                                            help="A link to the user representation video.\n"
                                            "Copy a link in an address bar from a youtube page contained corresponding video and paste here")
    user_description = fields.Html('Description for the website user', translate=True)
    location = fields.Char(string="Location", help="User Location")
    website_published = fields.Boolean(string="Show at Team Page", default=False)

    def youtube_url_validation(self, url):
        youtube_regex = (
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        if url is False:
            youtube_regex_match = False
        else:
            youtube_regex_match = re.match(youtube_regex, url)

        if youtube_regex_match:
            return youtube_regex_match.group(6)
        return None

    def twitter_url_validation(self, url):
        twitter_regex = (
            r'(https?://)?(www\.)?(twitter.com)/@?_?([a-z0-9]+_?)')
        if url is False:
            twitter_regex_match = False
        else:
            twitter_regex_match = re.match(twitter_regex, url)

        if twitter_regex_match:
            return twitter_regex_match.group(0)
        return False

    def upwork_url_validation(self, url):
        upwork_regex = (
            r'(https?://)?(www\.)?(upwork.com)/fl/([a-z]+)')
        if url is False:
            upwork_regex_match = False
        else:
            upwork_regex_match = re.match(upwork_regex, url)

        if upwork_regex_match:
            return upwork_regex_match.group(0)
        return False

    def github_name_validation(self, name):
        github_regex = (
            r'^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$')
        if name is False:
            github_regex_match = False
        else:
            github_regex_match = re.match(github_regex, name)

        if github_regex_match:
            return github_regex_match.group(0)
        return False

    @api.constrains('presentation_youtube_link')
    def _check_youtube_id(self):
        if self.presentation_youtube_link is not False and self.get_youtube_id(self.presentation_youtube_link) is False:
            raise UserError(_('Youtube link is incorrect.'))

    def get_youtube_id(self, link):
        link_id = self.youtube_url_validation(link)
        if link_id is None:
            return False
        return "https://www.youtube.com/embed/" + link_id + "?rel=0&amp;showinfo=0"

    def get_alias_mail(self):
        return self.email if self.login else False

    @api.constrains('username_twitter')
    def _check_twitter_link(self):
        if self.username_twitter is not False and self.twitter_url_validation(self.username_twitter) is False:
            raise UserError(_('Twitter link is incorrect.'))

    @api.constrains('url_upwork')
    def _check_upwork_link(self):
        if self.url_upwork is not False and self.upwork_url_validation(self.url_upwork) is False:
            raise UserError(_('Upwork link is incorrect.'))

    @api.constrains('username_github')
    def _check_github(self):
        if self.username_github is not False and self.github_name_validation(self.username_github) is False:
            raise UserError(_('Github name is incorrect.'))


class ResCompany(models.Model):
    _inherit = ['res.company']

    def _default_team_website_description_top_block(self):
        return '<h1 class="team_header"><span class="team_sub_header">'+self.env.user.company_id.name+'</span> team</h1>'

    team_website_description = fields.Html('Website Team Description', translate=True,
                                           help="Common html for team member pages")
    team_website_description_top_block = fields.Html('Website Team Description Top Block', translate=True,
                                                     help="Common html in the top block for the team members list page",
                                                     default=_default_team_website_description_top_block)
    team_website_description_bottom_block = fields.Html('Website Team Description Bottom Block', translate=True,
                                                        help="Common html in the bottom block for the team members list page")
