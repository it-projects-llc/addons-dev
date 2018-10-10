# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import uuid

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    namespace_ids = fields.Many2many('openapi.namespace', string='Allowed Integrations')
    token = fields.Char('Identification token',
                        default=lambda self: self._get_unique_token(),
                        required=True, copy=False)

    _sql_constraints = [
        ('token_uniq',
         'unique (token)',
         'A user already exists with this token. User\'s token must be unique!')
    ]

    @api.multi
    def reset_token(self):
        for record in self:
            record.write({'token': self._get_unique_token()})

    def _get_unique_token(self):
        token = str(uuid.uuid4())
        while self.search([('token', '=', token)]).exists():
            token = str(uuid.uuid4())
        return token

    @api.multi
    @api.constrains('token')
    def token_update(self):
        for record in self:
            if len(self.search([('token', '=', record.token)])) > 1:
                record.reset_token()

    @api.model
    def reset_all_tokens(self):
        self.search([]).reset_token()
