# -*- coding: utf-8 -*-
{
    "name": "Customers membership",
    "summary": """Loyalty membership""",
    "category": "Customers",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    # 'price': 40000.00,
    # 'currency': 'EUR',

    "depends": [
        "base",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/partner.xml",
        "views/membership.xml",
        "security/records.xml",
        "security/ir.model.access.csv",
    ],
    "qweb": [
    ],
    "demo": [],
    'installable': True,
    "auto_install": False,
}
