# -*- coding: utf-8 -*-
{
    "name": "Custom system for car renting",
    "summary": """Fleet leasing and management""",
    "category": "Managing vehicles and contracts",
    "images": ['images/1.jpg'],
    "version": "1.0.0",

    "author": "IT-Projects LLC",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    # 'price': 40000.00,
    # 'currency': 'EUR',

    "depends": [
        "hr",
        "fleet"
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/views.xml",
        "records.xml"
    ],
    "qweb": [
    ],
    "demo": [],
    'installable': True,
    "auto_install": False,
}
