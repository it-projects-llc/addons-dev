# -*- coding: utf-8 -*-
{
    "name": "Attachment Url Kingfisher Pro (Technical module)",
    "summary": """Technical module for compatibility ir_attachment_url and kingfisher_pro modules""",
    "category": "Tools",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Dinar Gabbasov",
    'website': "https://twitter.com/gabbasov_dinar",
    "license": "AGPL-3",
    # "price": 0.00,
    # "currency": "EUR",

    "depends": [
        "ir_attachment_s3",
        "kingfisher_pro",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/assets.xml",
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
