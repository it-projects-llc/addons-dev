# -*- coding: utf-8 -*-
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": """Laundry/Dry Cleaning Managment""",
    "summary": """Allows manage laundry/dry cleaning managment""",
    "category": "Point of Sale",
    # "live_test_url": "",
    "images": [],
    "version": "10.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Kolushov Alexandr",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/KolushovAlexandr",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "pos_pricelist",
        "kingrun_cusomization",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/assets.xml",
        "views/views.xml",
    ],
    "demo": [
    ],
    "qweb": [
        "static/src/xml/templates.xml",
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,
}
