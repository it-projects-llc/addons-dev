# -*- coding: utf-8 -*-
# Copyright 2018, XOE Solutions
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

"""Pinguin module for Odoo REST Api.

This module implements plumbing code to the REST interface interface concerning
authentication, validation, ORM access and error codes.

It also implements a ORP API worker in the future (maybe).

Todo:
    * Implement API worker
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html
"""

import werkzeug.wrappers

from collections import OrderedDict
try:
    import simplejson as json
except ImportError:
    import json

from odoo import http
from odoo.http import request, OpenERPSession
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED

####################################
# Definition of global error codes #
####################################

# 2xx Success
CODE__success = 200
CODE__created = 201
CODE__accepted = 202
CODE__ok_no_content = 204
# 4xx Client Errors
CODE__server_rejects = (400, "Server rejected", "Welcome to macondo!")
CODE__no_user_auth = (401, "Authentication",
                      "Your token could not be authenticated.")
CODE__user_no_perm = (401, "Permissions", "%s")
CODE__method_blocked = (403, "Blocked Method",
                        "This method is not whitelisted on this model.")
CODE__db_not_found = (404, "Db not found", "Welcome to macondo!")
CODE__canned_ctx_not_found = (404, "Canned context not found", "The requested canned context is not configured on this model")
CODE__obj_not_found = (404, "Object not found",
                       "This object is not available on this instance.")
CODE__res_not_found = (404, "Resource not found",
                       "There is no resource with this id.")
CODE__act_not_executed = (409, "Action not executed",
                          "The requested action was not executed.")
# 5xx Server errors
CODE__invalid_method = (501, "Invalid Method",
                        "This method is not implemented.")
CODE__invalid_spec = (501, "Invalid Field Spec",
                      "The field spec supplied is not valid.")
# If API Workers are enforced, but non is available (switched off)
CODE__no_api_worker = (503, "API worker sleeping",
                       "TThe API worker is currently not at work.")


def successful_response(status, data):
    """Successful respones wrapper.

    Args:
        status (int): The sucess code.
        data (str): The json object.

    Returns:
        Response: The werkzeug `response object`_.

    .. _response object:
        http://werkzeug.pocoo.org/docs/0.14/wrappers/#module-werkzeug.wrappers

    """
    return werkzeug.wrappers.Response(
        status=status,
        content_type='application/json; charset=utf-8',
        response=json.dumps(data),
    )


def error_response(status, error, error_descrip):
    """Successful respones wrapper.

    Args:
        status (int): The sucess code.
        error (str): The error summary.
        error_descrip (str): The error description.

    Returns:
        Response: The werkzeug `response object`_.

    .. _response object:
        http://werkzeug.pocoo.org/docs/0.14/wrappers/#module-werkzeug.wrappers

    """
    return werkzeug.wrappers.Response(
        status=status,
        content_type='application/json; charset=utf-8',
        response=json.dumps({
            'error': error,
            'error_descrip': error_descrip,
        }),
    )


##########################
# Pinguin Authentication #
##########################


# Server wide auth
def authenticate_token_for_server(token):
    """Extract and validate the encoded server salt conveyed by the token.

    Args:
        token (string): The raw access token.

    Returns:
        bool: True if server accepts the token, False otherwise.
    """
    return True  # TODO


# Database detection
def infer_database(token):
    """Extract and validate the encoded database information
    conveyed by the token.

    Args:
        token (string): The raw access token.

    Returns:
        str: The database name in clear text.

    Todo:
        - Validate against registries of the current thread.
        - Do NOT init a new registry by default, even if database exists.
        - Only load the registry if we are on a special API serving worker 
          with lower than regular HTTP worker priority (nice=5)
    """

    return 'test'  # TODO


# User token auth (db-scoped)
def authenticate_token_for_user(token):
    """Authenticate against the database and setup user session corresponding to the token.

    Args:
        token (string): The raw access token.

    Returns:
        bool: True if token is authorized for the requested user, False otherwise.

    Todo:
        - Return session instead?
    """
    return True  # TODO


# Namespace token auth (db-scoped)
def authenticate_token_for_namespace(namespace, token):
    """Validate token against the requested namespace.

    Args:
        namespace (string): The requested namespace.
        token (string): The raw access token.

    Returns:
        bool: True if token is authorized for the requested namespace, False otherwise.
    """
    return True


###################
# Pinguin Routing #
###################


# Patched http route
def pinguin_route(*args, **kwargs):
    """Set up the environment for rout handlers.

    Patches the framework and additionally authenticates
    the API token and infers database through a different mechanism.

    Args:
        *args: Transparent pass through to the patched method.
        **kwargs: Transparent pass through to the patched method.

    Returns:
        wrapped method: Wrapped
    """
    if not authenticate_token_for_server():
        # Second line of defense after WAP and before touching database
        # To (temporarily) cycle all tokens, change the server wide salt.
        # Security by obscurity...
        error_response(*CODE__server_rejects)
    db_name = infer_database()
    return http.route(*args, **kwargs)


############################
# Pinguin Metadata Helpers #
############################


# TODO: cache per model and database
# Get the specific context(openapi.access)
def get_create_context(namespace, model, canned_context):
    """Get the requested preconfigured context of the model specification.

    The canned context is used to preconfigure default values or context flags.
    That are used in a repetitive way in namespace for specific model.

    As this should, for performance reasons, not repeatedly result in calls to the persistence
    layer, this method is cached in memory.

    Args:
        namespace (str): The namespace to also validate against.
        model (str): The model, for which we retrieve the configuration.
        canned_context (str): The preconfigured context, which we request.

    Returns:
        dict: A dictionary containing the requested context.

    """
    # Token is not authorized on this namespace
    cr, uid = request.cr, request.session.uid

    # Singleton by construction (_sql_constraints)
    openapi_access = request.env(cr, uid)['openapi.access'].search(
        [('model_id', '=', model), ('namespace_id.name', '=', namespace)])

    assert len(openapi_access) == 1, "'openapi_access' is not a singleton, bad construction."
    # Singleton by construction (_sql_constraints)
    context = openapi_access.create_context_ids.filtered(lambda r: r['name'] == canned_context)
    assert len(context) == 1, "'context' is not a singleton, bad construction."

    if not context:
        return error_response(*CODE__canned_ctx_not_found)

    return context

# TODO: cache per model and database
# Get model configuration (openapi.access)
def get_model_openapi_access(namespace, model):
    """Get the model configuration and validate the requested namespace against the session.

    The namespace is a lightweight ACL + default implementation to integrate
    with various integration consumer, such as webstore, provisioning platform, etc.

    We validate the namspace at this later stage, because it forms part of the http route.
    The token has been related to a namspace already previously
    (:meth:`authenticate_token_for_namespace`).

    This is a double purpose method.

    As this should, for performance reasons, not repeatedly result in calls to the persistence
    layer, this method is cached in memory.

    Args:
        namespace (str): The namespace to also validate against.
        model (str): The model, for which we retrieve the configuration.

    Returns:
        Response: The error response object if namspace validation failed.
        dict: A dictionary containing the model API configuration for this namespace.
            The layout of the dict is as follows:
            ```python
            {'context':                 (Dict)      odoo context (default values through context),
            'out_fields_read_multi':    (Tuple)     field spec,
            'out_fields_read_one':      (Tuple)     field spec,
            'out_fields_create_one':    (Tuple)     field spec,
            'method' : {
                'public' : {
                     'mode':            (String)    one of 'all', 'none', 'custom',
                     'whitelist':       (List)      of method strings,
                 },
                'private' : {
                     'mode':            (String)    one of 'none', 'custom',
                     'whitelist':       (List)      of method strings,
                 },
            }
            ```

    """
    # Token is not authorized on this namespace
    if not TRUE:
        err = list(CODE__user_no_perm)
        err[2] = "The requested namespace (integration) is not authorized."
        return error_response(*err)

    cr, uid = request.cr, request.session.uid
    # Singleton by construction (_sql_constraints)
    openapi_access = request.env(cr, uid)['openapi.access'].search(
        [('model_id', '=', model), ('namespace_id.name', '=', namespace)])

    # TODO write transformation
    res = {
        'context': {}, # Take ot here
        'out_fields_read_multi': (),
        'out_fields_read_one': (),
        'out_fields_create_one': (),
        'method': {
            'public': {
                'mode': '',
                'whitelist': []
            },
            'private': {
                'mode': '',
                'whitelist': []
            }
        }
    }
    # Infer public method mode
    if openapi_access.api_public_methods and openapi_access.public_methods:
        res['method']['public']['mode'] = 'custom'
        res['method']['public']['whitelist'] = []
    elif openapi_access.api_public_methods:
        res['method']['public']['mode'] = 'all'
    else:
        res['method']['public']['mode'] = 'none'

    # Infer private method mode
    if openapi_access.private_methods:
        res['method']['private']['mode'] = 'custom'
        res['method']['private']['whitelist'] = []
    else:
        res['method']['private']['mode'] = 'none'

    return res


def validate_extra_field(field):
    """Validates extra fields on the fly.

    Args:
        field (str): The name of the field.
    Returns:
        none,Response: None, if validated, a error response else.
    """
    if not isinstance(field, basestring):
        error_response(*CODE__invalid_spec)


def validate_spec(model, spec):
    """Validates a spec for a given model.

    Args:
        model (:obj:`Model`): The model aginst which to validate.
        none,raise: None, if validated, raises else.
    """
    self = model
    for field in spec:
        if isinstance(field, tuple):
            # Syntax checks
            if len(field) != 2:
                raise "Tuples representing fields must have length 2. (%r)" % field
            if not isinstance(field[1], (tuple, list)):
                raise """Tuples representing fields must have a tuple wrapped in
                    a list or a bare tuple as it's second item. (%r)""" % field
            # Validity checks
            fld = self._fields[field]
            if not fld.relational:
                raise "Tuples representing fields can only specify relational fields. (%r)" % field
            if isinstance(field[1],
                          tuple) and fld.type in ['one2many', 'many2many']:
                raise "Specification of a 2many record cannot be a bare tuple. (%r)" % field
        else:
            raise "Fields are represented by either a strings or tulples. Found: %r" % type(
                field)


##################
# Pinguin Worker #
##################

#######################
# Pinguin ORM Wrapper #
#######################


# Dict from model
def get_dict_from_model(model, spec, id, **kwargs):
    """Fetch dictionary from one record according to spec.

    Args:
        model (:obj:`Model`): The model aginst which to validate.
        spec (:obj:`Tuple`): The spec to validate.
        id (int): The id of the record.
        **kwargs['include_fields'] (:obj:`Tuple`): The extra fields.
            This parameter is not implemented on higher level code in order
            to serve as a soft ACL implementation on top of the framework's
            own ACL.
        **kwargs['exclude_fields'] (:obj:`Tuple`): The excluded fields.

    Returns:
        dict: The python dictionary of the requested values.
    """
    include_fields = kw.get(
        'include_fields',
        ())  # Not actually implemented on higher level (ACL!)
    exclude_fields = kw.get('exclude_fields', ())

    model_obj = get_model_for_read(model)

    try:
        record = model_obj.browse([id])
    except:
        error_response(*CODE__res_not_found)
    return get_dict_from_record(record, spec, include_fields, include_fields)


# List of dicts from model
def get_dictlist_from_model(model, spec, **kwargs):
    """Fetch dictionary from one record according to spec.

    Args:
        model (:obj:`Model`): The model aginst which to validate.
        spec (:obj:`Tuple`): The spec to validate.
        **kwargs['domain'] (:obj:`Framework Domain`): The domain to filter on.
        **kwargs['offset'] (int): The offset of the queried records.
        **kwargs['limit'] (int): The limit to query.
        **kwargs['order'] (str): The postgres order string.
        **kwargs['include_fields'] (:obj:`Tuple`): The extra fields.
            This parameter is not implemented on higher level code in order
            to serve as a soft ACL implementation on top of the framework's
            own ACL.
        **kwargs['exclude_fields'] (:obj:`Tuple`): The excluded fields.

    Returns:
        list: The list of python dictionaries of the requested values.
    """
    domain = kw.get('domain', [])
    offset = kw.get('offset', 0)
    limit = kw.get('limit', None)
    order = kw.get('order', None)
    include_fields = kw.get(
        'include_fields',
        ())  # Not actually implemented on higher level (ACL!)
    exclude_fields = kw.get('exclude_fields', ())

    model_obj = get_model_for_read(model)

    records = model_obj.search(domain, offset=offset, limit=limit, order=order)

    # Do some optimization for subfields
    _prefetch = {}
    for field in spec:
        if isinstance(field, basestring):
            continue
        _fld = records._fields[field[0]]
        if _fld.relational:
            _prefetch[_fld.comodel] = records.mapped(field[0]).ids

    for mod, ids in _prefetch.iteritems():
        get_model_for_read(mod).browse(ids).read()

    result = []
    for record in records:
        result += [
            get_dict_from_record(record, spec, include_fields, exclude_fields)
        ]

    return result

# Get a model with special context
def get_model_for_read(model):
    """Fetch a model object from the environment opitimized for read.

    Postgres serialization levels are changed to allow parallel read queries.
    To increase the overall efficiency, as it is unlikely this API will be used
    as a mass transactional interface. Rather we asume sequential and structured
    integration workflows.

    Args:
        model (str): The model to retrieve from the environment.

    Returns:
        Model: The framework model.
        Response: The error response object.
    """
    cr, uid = request.cr, request.session.uid
    # Permit parallel query execution on read
    # Contrary to ISOLATION_LEVEL_SERIALIZABLE as per Odoo Standard
    cr._cnx.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
    try:
        return request.env(cr, uid)[model]
    except KeyError:
        error_response(*CODE__obj_not_found)

# Python > 3.5
# def get_dict_from_record(record, spec: tuple, include_fields: tuple, exclude_fields: tuple):

# Extract nested values from a record
def get_dict_from_record(record, spec, include_fields, exclude_fields):
    """Generates nested pyton dict representing one record.

    Going down to the record level, as the framework does not support nested
    data queries natively as they are typical for a REST API.

    Args:
        record (:obj:`RecordSet`): The singleton record to load.
        spec (:obj:`Tuple`): The field spec to load.
        include_fields (:obj:`Tuple`): The extra fields.
        exclude_fields (:obj:`Tuple`): The excluded fields.


    Returns:
        dict: The python dictionary representing the record according to the field spec.
    """
    (include_fields + exclude_fields).map(validate_extra_field)
    result = OrderedDict([])
    _spec = [fld for fld in spec
             if fld not in exclude_fields] + list(include_fields)
    for field in _spec:
        if isinstance(field, tuple):
            # It's a 2many (or a 2one specified as a list)
            if isinstance(field[1], list):
                result[field] = []
                for rec in record[field[0]]:
                    result[field] += [
                        get_dict_from_record(rec, field[1], [], [])
                    ]
            # It's a 2one
            if isinstance(field[1], tuple):
                assert len(record[field[
                    0]]) == 1, "A bare tuple, cannot spec a 2many field"
                result[field] = get_dict_from_record(record[field[0]],
                                                     field[1], [], [])
        # Normal field, or unspecified relational
        elif isinstance(field, (str, unicode)):
            result[field] = record.get(field, None)
    return result
