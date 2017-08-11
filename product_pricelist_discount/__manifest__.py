# -*- coding: utf-8 -*-
{
    "name": """Product Pricelist Technical module""",
    "summary": """Extends the functionality of the module Products & Pricelists""",
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
        "pos_pricelist",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/product_pricelist_discount_views.xml",
    ],
    "qweb": [
    ],
    "demo": [],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
