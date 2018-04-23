# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


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

    @api.multi
    def name_get(self):
        return [(record.id, "/api/v1/%s%s" % (record.name,
                                              ' (%s)' % record.description
                                              if record.description else ''))
                for record in self]
