# -*- coding: utf-8 -*-
{
    "name": """Product categories discount in POS""",
    "summary": """Product categories discount in POS""",
    "category": "Point of Sale",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "website": "https://twitter.com/gabbasov_dinar",
    "license": "AGPL-3",
    # "price": 0.00,
    # "currency": "EUR",

    "depends": [
        'point_of_sale',
        'pos_discount',
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views/template.xml',
        'views/view.xml',
    ],
    'qweb': [
        'static/src/xml/DiscountProgram.xml',
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
