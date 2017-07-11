# -*- coding: utf-8 -*-

from openerp import models, fields, api
import re


class Users(models.Model):
    _inherit = ['res.users']
    username_github = fields.Char(default=None)
    url_upwork = fields.Char(default=None)
    username_twitter = fields.Char()
    username_work_email = fields.Char(default=None)
    presentation_youtube_link = fields.Char()

    def youtube_url_validation(self, url):
        youtube_regex = (
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        youtube_regex_match = re.match(youtube_regex, url)

        if youtube_regex_match:
            return youtube_regex_match.group(6)
        return None

    def get_youtube_id(self, link):

        link_id = self.youtube_url_validation(link)

        if link_id is None:
            return False
        return "https://www.youtube.com/embed/" + link_id + "?rel=0&amp;showinfo=0"
