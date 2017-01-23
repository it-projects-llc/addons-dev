# -*- coding: utf-8 -*-
{
    "name": """Order Notes in POS""",
    "summary": """Order Notes in POS""",
    "category": "Point of Sale",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "website": "https://twitter.com/gabbasov_dinar",
    "license": "AGPL-3",
    # "price": 0.00,
    # "currency": "EUR",

    "depends": [
        'pos_restaurant',
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views/views.xml',
        'views/template.xml',
    ],
    'qweb': [],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
