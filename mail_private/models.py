# -*- coding: utf-8 -*-

from openerp import fields, models


class mail_compose_message(models.TransientModel):
    _inherit = 'mail.compose.message'

    is_internal = fields.Boolean('Send Internal Message')
