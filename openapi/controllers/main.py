# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Rafis Bikbov <https://it-projects.info/team/bikbov>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import json
import logging
from collections import OrderedDict

import werkzeug
from odoo import http

from odoo.http import content_disposition
from odoo.addons.web_settings_dashboard.controllers.main \
    import WebSettingsDashboard

_logger = logging.getLogger(__name__)


class OpenapiWebSettingsDashboard(WebSettingsDashboard):

    @http.route('/web_settings_dashboard/data', type='json', auth='user')
    def web_settings_dashboard_data(self, **kw):

        result = super(OpenapiWebSettingsDashboard, self)\
            .web_settings_dashboard_data(**kw)

        # dummy data for a while
        dummy = {
            'models_count': 123,
            'create_count': 10,
            'read_count': 123,
            'update_count': 55,
            'delete_count': 0,
            'last_connection': '2018-01-01 12:12:12',
        }

        def copy(obj, **d):
            return dict(obj.items() + d.items())

        namespace_list = [
            copy(dummy, name='magento'),
            copy(dummy, name='ebay'),
            copy(dummy, name='1c'),
        ]

        result.update({'openapi': {
            'namespace_list': namespace_list,
        }})

        return result


class OAS(http.Controller):

    @http.route('/api/v1/<namespace_name>/swagger.json',
                type='http', auth='public', csrf=False)
    def OAS_json_spec_download(self, namespace_name, **kwargs):
        namespace = http.request.env['openapi.namespace'].sudo().search([
            ('name', '=', namespace_name), ('token', '=', kwargs.get('token', ''))
        ])
        if not namespace:
            raise werkzeug.exceptions.NotFound()

        spec = namespace.get_OAS_part()

        ORDERED_SWAGGER_MAIN_PROPERTIES = [
            'swagger',  # 'string'
            'info',  # 'Info Object'
            'host',  # 'string'
            'basePath',  # 'string'
            'schemes',  # ['string']
            'consumes',  # ['string']
            'produces',  # ['string']
            'paths',  # 'Paths Object'
            'definitions',  # 'Definitions Object'
            'parameters',  # 'Parameters Definitions Object'
            'responses',  # 'Responses Definitions Object'
            'securityDefinitions',  # 'Security Definitions Object'
            'security',  # ['Security Requirement Object']
            'tags',  # ['Tag Object']
            'externalDocs',  # 'External Documentation Object'
        ]

        sorted_spec = OrderedDict([
            (property_name, spec[property_name])
            for property_name in ORDERED_SWAGGER_MAIN_PROPERTIES
            if spec.get(property_name)
        ])

        response_params = {
            'headers': [('Content-Type', 'application/json')]
        }
        if 'download' in kwargs:
            response_params['headers'] = [
                ('Content-Type', 'application/octet-stream; charset=binary'),
                ('Content-Disposition', content_disposition('swagger.json')),
            ]
            response_params['direct_passthrough'] = True

        return werkzeug.wrappers.Response(
            json.dumps(sorted_spec),
            status=200,
            **response_params
        )
