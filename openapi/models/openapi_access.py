# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Rafis Bikbov <https://it-projects.info/team/bikbov>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import json
import urllib
import inspect

from odoo import models, fields, api, _, exceptions

from ..controllers import pinguin

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
        'Private methods are ones that start with underscore. '
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

    @api.multi
    @api.constrains('public_methods')
    def _check_public_methods(self):
        for access in self:
            for line in access.public_methods.split('\n'):
                if not line:
                    continue
                if line.startswith('_'):
                    raise exceptions.ValidationError(_(
                        'Private method (starting with "_" listed in public methods whitelist)'))
                if line not in self._get_method_list():
                    raise exceptions.ValidationError(_(
                        'Method %r is not part of the model\'s method list:\n %r') % (
                        line, self._get_method_list()))

    @api.multi
    @api.constrains('private_methods')
    def _check_private_methods(self):
        for access in self:
            for line in access.private_methods.split('\n'):
                if not line:
                    continue
                if not line.startswith('_'):
                    raise exceptions.ValidationError(_(
                        'Public method (not starting with "_" listed in private methods whitelist'))
                if line not in self._get_method_list():
                    raise exceptions.ValidationError(_(
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

    @api.multi
    def get_OAS_paths_part(self, definition_prefix=''):
        for record in self:
            model_name = record.model
            read_many_path = '/%s' % model_name
            # uncomment if spec['basePath'] not will be contain namespace
            # read_many_path = '/%s/%s' % (record.namespace_id.name, model_name)
            read_one_path = '%s/{%s.id}' % (read_many_path, model_name)

            read_many_definition_ref = "#/definitions/%s" % pinguin.get_definition_name(record.model, definition_prefix, 'read_many')
            read_one_definition_ref = "#/definitions/%s" % pinguin.get_definition_name(record.model, definition_prefix, 'read_one')

            capitalized_model_name = ''.join([s.capitalize() for s in model_name.split('.')])

            paths_object = {
                read_many_path: {},
                read_one_path: {},
            }

            if record.api_create:
                paths_object[read_many_path]['post'] = {
                    "summary": "Add a new %s object to the store" % model_name,
                    "description": "",
                    "operationId": "add%s" % capitalized_model_name,
                    "consumes": [
                        "application/json",
                    ],
                    "produces": [
                        "application/json"
                    ],
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "description": "%s object that needs to be added to the store" % model_name,
                            "required": True,
                            "schema": {
                                "$ref": read_one_definition_ref
                            }
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "successful create",
                            "schema": {
                                "$ref": "#/definitions/%s-read_one" % model_name
                            }
                        },
                        "405": {
                            "description": "Invalid input"
                        },
                    },
                }

            if record.api_read:
                paths_object[read_many_path]['get'] = {
                    "summary": "Get all %s objects" % model_name,
                    'description': 'Returns all %s objects' % model_name,
                    "operationId": "getAll%s" % capitalized_model_name,
                    "produces": [
                        "application/json"
                    ],
                    "responses": {
                        "200": {
                            "description": "A list of %s." % model_name,
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": read_many_definition_ref
                                }
                            }
                        }
                    }
                }

                paths_object[read_one_path]['get'] = {
                    "summary": "Get %s by ID" % model_name,
                    "description": "Returns a single %s" % model_name,
                    "operationId": "get%sById" % capitalized_model_name,
                    "produces": [
                        "application/json"
                    ],
                    "parameters": [
                        {
                            "name": "%s.id" % model_name,
                            "in": "path",
                            "description": "ID of %s to return" % model_name,
                            "required": True,
                            "type": "integer",
                            "format": "int64"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "successful operation",
                            "schema": {
                                "$ref": read_one_definition_ref
                            }
                        },
                        "404": {
                            "description": "%s not found" % model_name
                        }
                    }
                }

            if record.api_update:
                paths_object[read_one_path]['put'] = {
                    "summary": "Update %s by ID" % model_name,
                    "description": "",
                    "operationId": "update%sById" % capitalized_model_name,
                    "produces": [
                        "application/json"
                    ],
                    "parameters": [
                        {
                            "name": "%s.id" % model_name,
                            "in": "path",
                            "description": "ID that need to be updated",
                            "required": True,
                            "type": "integer",
                            "format": "int64"
                        },
                        {
                            "in": "body",
                            "name": "body",
                            "description": "Updated %s object" % model_name,
                            "required": True,
                            "schema": {
                                "$ref": read_one_definition_ref
                            }
                        }
                    ],
                    "responses": {
                        "204": {
                            "description": "successful update",
                        },
                        "404": {
                            "description": "%s not found" % model_name
                        }
                    }
                }

            if record.api_delete:
                paths_object[read_one_path]['delete'] = {
                    "summary": "Delete %s by ID" % model_name,
                    "description": "",
                    # "description": "This can only be done by the user with special access.",
                    "operationId": "delete%s" % capitalized_model_name,
                    "produces": [
                        "application/json"
                    ],
                    "parameters": [
                        {
                            "name": "%s.id" % model_name,
                            "in": "path",
                            "description": "The ID that needs to be deleted",
                            "required": True,
                            "type": "integer",
                            "format": "int64"
                        }
                    ],
                    "responses": {
                        "204": {
                            "description": "successful delete"
                        },
                        "404": {
                            "description": "%s not found" % model_name
                        }
                    }
                }

            # remove the keys for which there are an empty value
            return {k: v for k, v in paths_object.items() if v}

    @api.multi
    def get_OAS_definitions_part(self):
        for record in self:
            related_model = record.env[record.model]
            export_fields_read_one = pinguin.transform_strfields_to_dict(record.read_one_id.export_fields.mapped('name'))
            export_fields_read_many = pinguin.transform_strfields_to_dict(record.read_many_id.export_fields.mapped('name'))
            definitions = {}
            definitions.update(pinguin.get_OAS_definitions_part(related_model, export_fields_read_one, definition_postfix='read_one'))
            definitions.update(pinguin.get_OAS_definitions_part(related_model, export_fields_read_many, definition_postfix='read_many'))
            return definitions

    @api.multi
    def get_OAS_part(self):
        for record in self:
            return {
                'definitions': record.get_OAS_definitions_part(),
                'paths': record.get_OAS_paths_part(),
            }


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

    @api.multi
    @api.constrains('context')
    def _check_context(self):
        for record in self:
            try:
                json.loads(record.context[1:-1])
            except ValueError:
                raise exceptions.ValidationError(_('Context must be jsonable.'))
