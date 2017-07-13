# -*- coding: utf-8 -*-

from openerp import models, fields
import re


class Users(models.Model):
    _inherit = ['res.users']

    username_github = fields.Char(default=None, string="Github", help="User GitHub name")
    url_upwork = fields.Char(default=None, string="Upwork link", help="User upwork link")
    username_twitter = fields.Char(string="Twitter link", help="User twitter link")
    username_work_email = fields.Char(default=None, string="Email address", help="User work email")
    presentation_youtube_link = fields.Char(string='YouTube representation video link',
                                            help="A link to the user representation video.\n"
                                            "Copy a link in an address bar from a youtube page contained corresponding video and paste here")
    user_description = fields.Html('Description for the website user', translate=True)

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

    def get_youtube_id(self, link):

        link_id = self.youtube_url_validation(link)

        if link_id is None:
            return False
        return "https://www.youtube.com/embed/" + link_id + "?rel=0&amp;showinfo=0"

    def get_alias_mail(self):

        if self.alias_name:
            alias_email_full = self.alias_name + "@" + self.alias_domain
            return alias_email_full

        else:
            return False
