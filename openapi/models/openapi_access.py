# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Rafis Bikbov <https://it-projects.info/team/bikbov>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import collections
import json
import urllib
import inspect

from odoo import models, fields, api, _, exceptions

from odoo.addons.openapi.controllers import pinguin


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

    _sql_constraints = [
        ('namespace_model_uniq',
         'unique (namespace_id, model_id)',
         'There is already a record for this Model')
    ]

    @api.model
    def _get_method_list(self):
        return {m[0] for m in inspect.getmembers(self.env[self.model], predicate=inspect.ismethod)}

    @api.multi
    @api.constrains('public_methods')
    def _check_public_methods(self):
        for access in self:
            if not access.public_methods:
                continue
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
            if not access.private_methods:
                continue
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

    @api.constrains('api_create', 'api_read', 'api_update', 'api_delete')
    def _check_methods(self):
        methods = [
            self.api_create,
            self.api_read,
            self.api_update,
            self.api_delete,
            self.api_public_methods,
        ]
        methods += (self.public_methods or '').split('\n')
        methods += (self.private_methods or '').split('\n')
        if all(not m for m in methods):
            raise exceptions.ValidationError(
                _('You must select at least one API method for "%s" model.') % self.model
            )

    @api.multi
    def name_get(self):
        return [(record.id, "%s/%s" % (record.namespace_id.name, record.model))
                for record in self]

    def get_OAS_paths_part(self):
        model_name = self.model
        read_many_path = '/%s' % model_name
        read_one_path = '%s/{id}' % read_many_path
        param_id_ref = "#/parameters/RecordIdInPath"

        read_many_definition_ref = "#/definitions/%s" % pinguin.get_definition_name(self.model, '', 'read_many')
        read_one_definition_ref = "#/definitions/%s" % pinguin.get_definition_name(self.model, '', 'read_one')

        capitalized_model_name = ''.join([s.capitalize() for s in model_name.split('.')])

        paths_object = collections.OrderedDict([
            (read_many_path, {}),
            (read_one_path, {}),
        ])

        if self.api_create:
            paths_object[read_many_path]['post'] = {
                "summary": "Add a new %s object to the store" % model_name,
                "description": "",
                "operationId": "add%s" % capitalized_model_name,
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
                    "400": {
                        "description": "invalid data",
                        "schema": {
                            "$ref": "#/definitions/ErrorResponse"
                        }
                    }
                },
            }

        if self.api_read:
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
                        '$ref': param_id_ref
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

        if self.api_update:
            paths_object[read_one_path]['put'] = {
                "summary": "Update %s by ID" % model_name,
                "description": "",
                "operationId": "update%sById" % capitalized_model_name,
                "parameters": [
                    {
                        '$ref': param_id_ref
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
                    "400": {
                        "description": "invalid data",
                        "schema": {
                            "$ref": "#/definitions/ErrorResponse"
                        }
                    },
                    "404": {
                        "description": "%s not found" % model_name
                    }
                }
            }

        if self.api_delete:
            paths_object[read_one_path]['delete'] = {
                "summary": "Delete %s by ID" % model_name,
                "description": "",
                "operationId": "delete%s" % capitalized_model_name,
                "produces": [
                    "application/json"
                ],
                "parameters": [
                    {
                        '$ref': param_id_ref
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

        if self.api_public_methods or self.public_methods or self.private_methods:
            allowed_methods = []
            if self.api_public_methods:
                allowed_methods += [m for m in self._get_method_list() if not m.startswith('_')]
            elif self.public_methods:
                allowed_methods += [m for m in self.public_methods.split('\n') if m]
            if self.private_methods:
                allowed_methods += [m for m in self.private_methods.split('\n') if m]
            allowed_methods = list(set(allowed_methods))

            params_one_ref = "#/parameters/MethodParams-single_record"
            params_many_ref = "#/parameters/MethodParams-recordset"

            for method_name in allowed_methods:
                read_one_path_method = '%s/%s' % (read_one_path, method_name)
                read_many_path_method = '%s/%s' % (read_many_path, method_name)

                paths_object[read_one_path_method] = {
                    'patch': {
                        "summary": "Patch %s by single ID" % model_name,
                        "description": "Call model method for single record.",
                        "operationId": "%sMethodCallFor%sSingleRecord" % (method_name, capitalized_model_name),
                        "consumes": [
                            "multipart/form-data",
                            "application/x-www-form-urlencoded",
                        ],
                        "produces": [
                            "application/json",
                        ],
                        "parameters": [
                            {
                                '$ref': param_id_ref
                            },
                            {
                                '$ref': params_one_ref
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "successful patch"
                            },
                        }
                    }
                }

                paths_object[read_many_path_method] = {
                    'patch': {
                        "summary": "Patch %s by some IDs" % model_name,
                        "description": "Call model method for recordset.",
                        "operationId": "%sMethodCallFor%sRecordset" % (method_name, capitalized_model_name),
                        "consumes": [
                            "multipart/form-data",
                            "application/x-www-form-urlencoded",
                        ],
                        "produces": [
                            "application/json",
                        ],
                        "parameters": [
                            {
                                '$ref': params_many_ref
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "successful patch"
                            },
                        }
                    }
                }

        for path_item_value in paths_object.values():
            for path_method in path_item_value.values():
                path_method.update({
                    'tags': [model_name]
                })

        return paths_object

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
        self = self.sudo()
        for record in self:
            return {
                'definitions': record.get_OAS_definitions_part(),
                'paths': record.get_OAS_paths_part(),
                'tag': {
                    "name": "%s" % self.model,
                    "description": "Everything about %s" % self.model,
                }
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
        Model = self.env[self.model_id.model]
        fields = Model.fields_get()
        for record in self:
            try:
                data = json.loads(record.context[1:-1])
            except ValueError:
                raise exceptions.ValidationError(_('Context must be jsonable.'))

            for k, v in data.items():
                if k.startswith('default_') and k[8:] not in fields:
                    raise exceptions.ValidationError(_('The model "%s" has no such field: "%s".') % (Model, k[8:]))
