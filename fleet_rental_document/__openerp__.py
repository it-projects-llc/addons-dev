# -*- coding: utf-8 -*-
{
    "name": """Fleet Rental Document""",
    "summary": """
    The module implements base part of all rental documents.""",
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
        "l10n_sa",
        "fleet_branch",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'security/ir.model.access.csv',
        'wizard/make_invoice.xml',
        "views/fleet_rental_document.xml",
        "views/fleet_rental_document_rent.xml",
        "views/fleet_rental_document_return.xml",
        "views/fleet_rental_check_vehicle.xml",
        "views/fleet.xml",
        "views/ir_sequence.xml",
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
