# -*- coding: utf-8 -*-
{
    "name": """Fleet Rental Return Document""",
    "summary": """
    Create Return documents, confirm returns and check vehicle rent payments""",
    "category": "Managing vehicles and contracts",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Ildar Nasyrov",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    #"price": 9.00,
    #"currency": "EUR",

    "depends": [
        "fleet",
        "fleet_rental_document",
        "fleet_rental_check_vehicle",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'security/ir.model.access.csv',
        "views/fleet_rental_document_return.xml",
    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
}
