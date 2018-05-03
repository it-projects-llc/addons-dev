# -*- coding: utf-8 -*-
# Copyright 2018, XOE Solutions
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import functools
import hashlib
import logging
import os
from ast import literal_eval
import base64

import odoo
from odoo import http, SUPERUSER_ID, models
from odoo.http import request, OpenERPSession
from odoo.modules.registry import RegistryManager
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED

from .pinguin import *

_logger = logging.getLogger(__name__)

#################################################################
# Odoo REST API                                                 #
#  Version 1                                                    #
# --------------------------------------------------------------#
# The current api version is considered stable, although        #
# the exposed models and methods change as they are configured  #
# on the database level. Only if significant changes in the api #
# generation logic should be implemented in the future          #
# a version bump should be considered.                          #
#################################################################

API_ENDPOINT = '/api'
API_ENDPOINT_V1 = '/v1'
# API_ENDPOINT_V2 = '/2'

# We patch the route decorator in pinguin.py
# with authentication and DB inference logic.
# We also check if the model is installed in the database.
# Furthermore we chacek if api version is suppported.
# This keeps the code below minial and readable.
http.route = pinguin_route


class ApiV1Controller(http.Controller):
    """ Implements the REST API V1 endpoint.
    .. methods:

        CRUD Methods:
        - `POST     .../<model>`               -> `CreateOne`
        - `PUT      .../<model>/<id>`          -> `UpdateOne`
        - `GET      .../<model>`               -> `ReadMulti`
        - `GET      .../<model>/<id>`          -> `ReadOne`
        - `DELETE   .../<model>/<id>`          -> `UnlinkOne`

        Auxiliary Methods:
        - `PATCH    .../<model>/<id>/<method>`               -> `Call Method on Singleton Record`
        - `PATCH    .../<model>/<method>`                    -> `Call Method on RecordSet`
        - `GET      .../report/pdf/<report_external_id>`     -> `Get Report as PDF`
        - `GET      .../report/html/<report_external_id>`    -> `Get Report as HTML`
    """

    _api_endpoint = API_ENDPOINT + API_ENDPOINT_V1
    _api_endpoint = _api_endpoint + '/<namespace>'
    # CreateOne # ReadMulti
    _api_endpoint_model = _api_endpoint + '/<model>'
    # ReadOne # UpdateOne # UnlikOne
    _api_endpoint_model_id = _api_endpoint + '/<model>/<id>'
    # Call Methods
    _api_endpoint_model_id_method = _api_endpoint + '/<model>/<id>/<method>'  # on Singleton Record
    _api_endpoint_model_method = _api_endpoint + '/<model>/<method>'  # on RecordSet
    # Get Reports
    _api_report_pdf = _api_endpoint + '/report/pdf/<report_external_id>'  # as PDF
    _api_report_html = _api_endpoint + '/report/html/<report_external_id>'  # as HTML


    ##################
    ## CRUD Methods ##
    ##################

    # CreateOne
    @http.route(
        _api_endpoint_model,
        methods=['POST'],
        type='http',
        auth='none',
        csrf=False)
    def create_one__POST(self, namespace, model):
        conf = get_model_openapi_access(namespace, model)
        # If context is not a python dict
        # TODO unwrap
        if isinstance(kw.get('context'), basestring):
            context = get_create_context(namespace, model, kw.get('context'))
        else:
            context = kw.get('context') or {}
        return wrap__resource__create_one(
            modelname=model,
            context=conf['context'],
            success_code=CODE__created,
            out_fields=conf['out_fields_create_one'])

    # ReadMulti (optional: filters, offset, limit, order, include_fields, exclude_fields):
    @http.route(_api_endpoint_model, methods=['GET'], type='http', auth='none')
    def read_multi__GET(self, namespace, model, **kw):
        conf = get_model_openapi_access(namespace, model)
        return wrap__resource__read_all(
            modelname=model,
            success_code=CODE__success,
            out_fields=conf['out_fields_read_multi'])

    # ReadOne (optional: include_fields, exclude_fields)
    @http.route(
        _api_endpoint_model_id, methods=['GET'], type='http', auth='none')
    def read_one__GET(self, namespace, model, id, **kw):
        conf = get_model_openapi_access(namespace, model)
        return wrap__resource__read_one(
            modelname=model,
            id=id,
            success_code=CODE__success,
            out_fields=conf['out_fields_read_one'])

    # UpdateOne
    @http.route(
        _api_endpoint_model_id,
        methods=['PUT'],
        type='http',
        auth='none',
        csrf=False)
    def update_one__PUT(self, namespace, model, id):
        _ = namespace
        return wrap__resource__update_one(
            modelname=model, id=id, success_code=CODE__ok_no_content)

    # UnlikOne
    @http.route(
        _api_endpoint_model_id,
        methods=['DELETE'],
        type='http',
        auth='none',
        csrf=False)
    def unlink_one__DELETE(self, namespace, model, id):
        return wrap__resource__unlink_one(
            modelname=model, id=id, success_code=CODE__ok_no_content)

    #######################
    ## Auxiliary Methods ##
    #######################

    # Call Method on Singleton Record (optional: method parameters)
    @http.route(
        _api_endpoint_model_id_method,
        methods=['PATCH'],
        type='http',
        auth='none',
        csrf=False)
    def call_method_one__PATCH(self, namespace, model, id, method):
        return wrap__resource__call_method(
            modelname=model,
            ids=[id],
            method=method,
            success_code=CODE__success)

    # Call Method on RecordSet (optional: method parameters)
    @http.route(
        _api_endpoint_model_method,
        methods=['PATCH'],
        type='http',
        auth='none',
        csrf=False)
    def call_method_mulit__PATCH(self, namespace, model, method, ids, **kw):
        return wrap__resource__call_method(
            modelname=model,
            ids=ids,
            method=method,
            success_code=CODE__accepted)

    # Get Report as PDF
    @http.route(_api_report_pdf, methods=['GET'], type='http', auth='none')
    def report_pdf__GET(self, namespace, report_external_id):
        return wrap__resource__call_method(
            modelname='report',
            ids=[1],
            method='get_html',
            success_code=CODE__success)

    # Get Report as HTML
    @http.route(_api_report_html, methods=['GET'], type='http', auth='none')
    def report_html__GET(self, namespace, report_external_id):
        return wrap__resource__call_method(
            modelname='report',
            ids=[1],
            method='get_pdf',
            success_code=CODE__success)
