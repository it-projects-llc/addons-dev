# -*- coding: utf-8 -*-
{
    "name": """POS Kitchen Screen""",
    "summary": """Use POS for sync with kitchen screen""",
    "category": "Point Of Sale",
    # "live_test_url": "",
    "images": [],
    "version": "10.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/GabbasovDinar",
    "license": "LGPL-3",
    # "price": 0.00,
    # "currency": "EUR",

    "depends": [
        "pos_multi_session",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "security/ir.model.access.csv",
        "views/pos_multi_session_kitchen_template.xml",
        "views/pos_config_view.xml",
        "views/pos_category_view.xml",
        "views/pos_multi_session_kitchen_view.xml",
    ],
    "qweb": [
        "static/src/xml/pos_multi_session_kitchen.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,
}
