# -*- coding: utf-8 -*-
# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": """Disable options in POS (restaurant extension)""",
    "summary": """Control access to POS restaurant options""",
    "category": "Point of Sale",
    # "live_test_url": "",
    "images": [],
    "version": "12.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/12.0/pos_disable_payment_restaurant/",
    "license": "LGPL-3",
    "price": 9.00,
    "currency": "EUR",

    "depends": [
        "pos_access_right",
        "pos_restaurant",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/template.xml",
        "security/res_groups.xml",
    ],
    "qweb": [
    ],
    "demo": [
        "demo/res_groups.xml",
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,
}
