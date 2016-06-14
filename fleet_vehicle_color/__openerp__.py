# -*- coding: utf-8 -*-
{
    "name": """Fleet Vehicle Color""",
    "summary": """Select vehicle color from predefined list of colors""",
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
#        "web_widget_color",
# TODO: port web_widget_color on 9.0
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/fleet_vehicle_color.xml",
        "views/fleet.xml",
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
