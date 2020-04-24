# Copyright 2020 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": """Website Locations""",
    "summary": """Website Locations""",
    "category": "eCommerce",
    # "live_test_url": "http://apps.it-projects.info/shop/product/website-multi-company?version=12.0",
    "images": [],
    "version": "12.0.1.0.0",
    "application": False,
    "author": "IT-Projects LLC, Kolushov Alexandr",
    "support": "apps@itpp.dev",
    "website": "https://it-projects.info/team/KolushovAlexandr",
    "license": "Other OSI approved licence",  # MIT
    # "price": 9.00,
    # "currency": "EUR",
    "depends": [
        "website_sale",
        "stock"
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/website_views.xml",
    ],
    "qweb": [],
    "demo": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "auto_install": False,
    "installable": True,
}
