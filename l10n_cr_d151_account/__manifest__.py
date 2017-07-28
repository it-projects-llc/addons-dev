# -*- coding: utf-8 -*-
{
    "name": """l10n_cr_d151_account""",
    "summary": """None""",
    "category": "None",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Artyom Losev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "license": "LGPL-3",

    "depends": [
        "account",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
    	"security/ir.model.access.csv",
        "views/d151_views.xml",
        "views/inherited_views.xml",
        "views/views.xml"
    ],
    "qweb": [],
    "demo": [
        "data/data_demo.xml",
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
