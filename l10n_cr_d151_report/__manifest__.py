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
        "l10n_cr_d151_account",
        "report_xlsx"
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
    	"views.xml",
        "l10n_cr_d151_report_report.xml"
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
