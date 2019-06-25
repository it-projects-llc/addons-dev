# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class SuggestServiceman(models.TransientModel):
    _name = 'suggest.serciceman.job'

    user_ids = fields.Many2many(
        'res.users',
        'user_id',
        'wizard_id',
        help='This field is a related user in suggest\
            best serviceman for user record.')
