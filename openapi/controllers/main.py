# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import http

from odoo.addons.web_settings_dashboard.controllers.main \
    import WebSettingsDashboard


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
