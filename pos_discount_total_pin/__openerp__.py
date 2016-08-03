# -*- coding: utf-8 -*-
{
    "name": """Restrict set discounts for all POS Orders""",
    "summary": """Set discount for all POS Orders can user has access only""",
    "category": "Point of Sale",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Pavel Romanchenko",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    #"price": 9.00,
    #"currency": "EUR",

    "depends": [
        'pos_discount_total',
        'pos_pin',
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views.xml',
        'data.xml',
    ],
    "qweb": [],
    "demo": [],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
