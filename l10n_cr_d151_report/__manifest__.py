# -*- coding: utf-8 -*-
{
    "name": """l10n_cr_d151_report""",
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
        "l10n_cr_d151_account"
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "d151_report.xml",
    	"views.xml",
        "report_template.xml",
    ],
    "qweb": [],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
