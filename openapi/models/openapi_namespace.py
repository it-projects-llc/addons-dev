# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Rafis Bikbov <https://it-projects.info/team/bikbov>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import urllib
import urlparse
import uuid

from odoo import models, fields, api
from ..controllers import pinguin


class Namespace(models.Model):

    _name = 'openapi.namespace'

    active = fields.Boolean('Active', default=True)
    name = fields.Char(
        'Name',
        required=True,
        help="""Integration name, e.g. ebay, amazon, magento, etc.
        The name is used in api endpoint""")
    description = fields.Char('Description')
    log_ids = fields.One2many('openapi.log', 'namespace_id', string='Logs')
    log_request = fields.Selection([
        ('disabled', 'Disabled'),
        ('info', 'Short'),
        ('debug', 'Full'),
    ], 'Log Requests', default='disabled')

    log_response = fields.Selection([
        ('disabled', 'Disabled'),
        ('error', 'Errors only'),
        ('debug', 'Full'),
    ], 'Log Responses', default='error')

    last_log_date = fields.Datetime(
        related='log_ids.create_date',
        string='Latest usage'
    )

    access_ids = fields.One2many('openapi.access', 'namespace_id', string='Accesses', context={'active_test': False})
    user_ids = fields.Many2many('res.users', string='Allowed Users', default=lambda self: self.env.user)

    token = fields.Char('Identification token',
                        default=lambda self: str(uuid.uuid4()), readonly=True,
                        required=True, copy=False)
    spec_url = fields.Char('Specification link', compute='_compute_spec_url')

    _sql_constraints = [
        ('name_uniq',
         'unique (name)',
         'A namespace already exists with this name. Namespace\'s name must be unique!')
    ]

    @api.multi
    def name_get(self):
        return [(record.id, "/api/v1/%s%s" % (record.name,
                                              ' (%s)' % record.description
                                              if record.description else ''))
                for record in self]

    @api.model
    def _fix_name(self, vals):
        if 'name' in vals:
            vals['name'] = urllib.quote_plus(vals['name'].lower())
        return vals

    @api.model
    def create(self, vals):
        vals = self._fix_name(vals)
        return super(Namespace, self).create(vals)

    @api.multi
    def write(self, vals):
        vals = self._fix_name(vals)
        return super(Namespace, self).write(vals)

    @api.multi
    def get_OAS_part(self):
        current_host = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        parsed_current_host = urlparse.urlparse(current_host)

        for record in self:
            spec = {
                "swagger": "2.0",
                "info": {
                    "title": "Swagger Sample App",
                    "version": "1.0.0"
                },
                "host": parsed_current_host.netloc,
                "basePath": "/api/v1/%s" % record.name,
                "schemes": [
                    parsed_current_host.scheme
                ],
            }
            for openapi_access in record.access_ids.filtered('active'):
                pinguin.update(spec, openapi_access.get_OAS_part())

            return spec

    @api.depends('name', 'token')
    def _compute_spec_url(self):
        for record in self:
            record.spec_url = "/api/v1/%s/swagger.json?token=%s" % (record.name, record.token)

    def reset_token(self):
        for record in self:
            token = str(uuid.uuid4())
            while self.search([('token', '=', token)]).exists():
                token = str(uuid.uuid4())
            record.write({'token': token})
