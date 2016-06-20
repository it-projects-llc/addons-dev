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
        "fleet",
        "account",
        "account_asset",
        "partner_person",
        "sale_membership",
        "fleet_rental_document",
        "fleet_rental_check_vehicle",
        "fleet_vehicle_color",
        "fleet_bill",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "security/records.xml",
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/partner.xml",
        "views/fleet.xml",
        "views/asset.xml",
        "views/transfer.xml",
        "views/user.xml",
    ],
    "qweb": [
    ],
    "demo": ['demo/demo.xml'],
    'installable': True,
    "auto_install": False,
}
