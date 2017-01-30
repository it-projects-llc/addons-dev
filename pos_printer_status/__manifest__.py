# -*- coding: utf-8 -*-
{
    "name": """Printer Status in POS""",
    "summary": """Printer Status in POS""",
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
        'views/template.xml',
        # 'views/view.xml',
    ],
    'qweb': [
        "static/src/xml/printer_status.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
