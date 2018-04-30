# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class Access(models.Model):
    _name = 'openapi.access'
    _description = 'Access via API '

    active = fields.Boolean('Active', default=True)
    namespace_id = fields.Many2one(
        'openapi.namespace',
        'Integration',
        required=True)
    model_id = fields.Many2one('ir.model', 'Model', required=True)
    model = fields.Char(related='model_id.model')
    api_create = fields.Boolean('Create via API', default=False)
    api_read = fields.Boolean('Read via API', default=False)
    api_update = fields.Boolean('Update via API', default=False)
    api_delete = fields.Boolean('Delete via API', default=False)
    # Options for Public methods:
    # * all forbidden
    # * all allowed
    # * some are allowed
    api_public_methods = fields.Boolean(
        'Call Public methods via API',
        default=False,
    )
    public_methods = fields.Text(
        'Restrict Public methods',
        help='Allowed public methods besides basic ones. '
        'Public methods are ones that don\'t start with underscore). '
        'Format: one method per line. '
        'When empty -- all public methods are allowed')
    # Options for Private methods
    # * all forbidden
    # * some are allowed
    private_methods = fields.Text(
        'Allow Private methods',
        help='Allowed private methods. '
        'Private methods are ones that start with undescore. '
        'Format: one method per line. '
        'When empty -- private methods are not allowed')
    read_one_id = fields.Many2one(
        'ir.exports',
        'Read One Fields',
        help='Fields to return on reading one record',
        domain="[('resource', '=', model)]")
    read_many_id = fields.Many2one(
        'ir.exports',
        'Read Many Fields',
        help='Fields to return on reading via non one-record endpoint',
        domain="[('resource', '=', model)]")
    create_context_ids = fields.Many2many(
        'openapi.access.create.context',
        string='Creation Context Presets',
        help="Can be used to pass default values or custom context",
        domain="[('model_id', '=', model_id)]",
        context="{'default_model_id': model_id}",
    )

    _sql_constraints = [
        ('namespace_model_uniq',
         'unique (namespace_id, model_id)',
         'There is already a record for this Model')
    ]

    @api.multi
    def name_get(self):
        return [(record.id, "%s/%s" % (record.namespace_id.name, record.model))
                for record in self]


class AccessCreateContext(models.Model):
    _name = 'openapi.access.create.context'
    _description = 'Context on creating via API '

    name = fields.Char('Name', required=True)
    description = fields.Char('Description')
    model_id = fields.Many2one('ir.model', 'Model', required=True)
    context = fields.Text('Context', required=True)
