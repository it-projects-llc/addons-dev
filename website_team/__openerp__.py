# -*- coding: utf-8 -*-
{
    "name": """Website Team""",
    "summary": """Team""",
    "category": "website",
    "images": [
        "static/src/img/3.png"
    ],
    "version": "1.0.0",
    "application": False,

    "author": "Kolushov",
    "license": "LGPL-3",

    "depends": [
        "website",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/template_user_card.xml",
        "views/users_page.xml",
        "views/assets.xml",
        "views/website_users_all.xml",
        "views/web_team.xml"

    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
