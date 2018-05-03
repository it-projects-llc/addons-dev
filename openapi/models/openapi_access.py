# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import urllib
import inspect

from odoo import models, fields, api, _
from odo.expressions import ValidationError


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

    @api.model
    def _get_method_list(self):
        return {m[0] for m in inspect.getmembers(self.env[self.model], predicate=inspect.ismethod)}

    @api.depends('public_methods')
    def check_public_methods(self):
        for access in self:
            if not access.check_public_methods:
                continue
            for line in access.check_public_methods.split('\n'):
                if line.startswith('_'):
                    ValidationError(_(
                        'Private method (starting with "_" listed in public methods whitelist'))
                if line not in self._get_method_list():
                    ValidationError(_(
                        'Method %r is not part of the model\'s method list:\n %r') % (
                        line, self._get_method_list()))

    @api.depends('private_methods')
    def check_private_methods(self):
        for access in self:
            for line in access.check_public_methods.split('\n'):
                if not line.startswith('_'):
                    ValidationError(_(
                        'Public method (not starting with "_" listed in private methods whitelist'))
                if line not in self._get_method_list():
                    ValidationError(_(
                        'Method %r is not part of the model\'s method list:\n %r') % (
                        line, self._get_method_list()))

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


    _sql_constraints = [
        ('context_model_name_uniq',
         'unique (name, model_id)',
         'There is already a context with the same name for this Model')
    ]

    @api.model
    def _fix_name(self, vals):
        if 'name' in vals:
            vals['name'] = urllib.quote_plus(vals['name'].lower())
        return vals

    @api.model
    def create(self, vals):
        vals = self._fix_name(vals)
        return super(AccessCreateContext, self).create(vals)

    @api.multi
    def write(self, vals):
        vals = self._fix_name(vals)
        return super(AccessCreateContext, self).write(vals)
