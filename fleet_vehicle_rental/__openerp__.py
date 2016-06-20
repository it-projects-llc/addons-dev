# -*- coding: utf-8 -*-
{
    "name": """Fleet Vehicle Rental""",
    "summary": """
    The module introduces rental fields in fleet_vehicle.""",
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
        "decimal_precision",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/fleet_vehicle_rental.xml",
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
