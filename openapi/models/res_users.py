# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import uuid

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    namespace_ids = fields.Many2many('openapi.namespace', string='Allowed Integrations')
    token = fields.Char('Identification token',
                        default=lambda self: str(uuid.uuid4()),
                        required=True, copy=False)

    _sql_constraints = [
        ('token_uniq',
         'unique (token)',
         'A user already exists with this token. User\'s token must be unique!')
    ]

    @api.multi
    def reset_token(self):
        for record in self:
            token = str(uuid.uuid4())
            while self.search([('token', '=', token)]).exists():
                token = str(uuid.uuid4())
            record.write({'token': token})
