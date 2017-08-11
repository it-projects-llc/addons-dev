# -*- coding: utf-8 -*-
{
    "name": """POS Advanced Discounts""",
    "summary": """Extends the functionality of the module POS Pricelist""",
    "category": "Point of Sale",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "support": "apps@it-projects.info",
    "website": "https://twitter.com/gabbasov_dinar",
    "license": "GPL-3",
    # "price": 0.00,
    # "currency": "EUR",

    "depends": [
        "product_pricelist_discount",
        "pos_category_multi",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/pos_advanced_discounts_template.xml",
    ],
    "qweb": [
        "static/src/xml/pos.xml",
    ],
    "demo": [],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
