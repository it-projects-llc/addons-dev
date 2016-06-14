# -*- coding: utf-8 -*-
{
    "name": """Fleet Check Vehicle""",
    "summary": """With this module you can create a list of items to be checked on the vehicle before and after rent. And then you can
    add a checklist with these items on a rental document. Thus you'll be sure that your employees has checked everything and clients
    sign that the items are checked.""",
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
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/fleet_rental_check_vehicle.xml",
        "views/fleet_rental_document.xml",
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
