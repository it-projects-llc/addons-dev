# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Yan Chirino <https://xoe.solutions/>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": """REST API / Open API (Swagger)""",
    "summary": """Set up API and export OpenAPI specification file for integration with whatever system you need""",
    "category": "",
    # "live_test_url": "",
    "images": [],
    "version": "12.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/yelizariev",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "web_tour",
        "web_settings_dashboard",
    ],
    "external_dependencies": {"python": ['bravado_core', 'swagger_spec_validator'], "bin": []},
    "data": [
        "views/assets.xml",
        "views/openapi_view.xml",
        "views/res_users_view.xml",
        "views/ir_model_view.xml",
        "security/user_groups.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
        "views/assets_demo.xml",
        "views/tour_views.xml",
        "data/openapi_demo.xml",
    ],
    "qweb": [
        "static/src/xml/dashboard.xml",
        # Сommented until we discuss it
        # "static/src/xml/configure_api_button.xml"
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,
}
