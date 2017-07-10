# -*- coding: utf-8 -*-

from openerp import fields
from openerp import models


class Users(models.Model):
    _inherit = ['res.users']
    username_github = fields.Char(default=None)
    url_upwork = fields.Char(default=None)
    username_twitter = fields.Char()
    username_work_email = fields.Char(default=None)
    username_youtube_link = fields.Char()
