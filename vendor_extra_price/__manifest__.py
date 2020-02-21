# Copyright 2020 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": """Vendor Extra Price""",
    "summary": """""",
    "category": "Point of Sale",
    # "live_test_url": "",
    "images": [],
    "version": "12.0.1.0.0",
    "application": False,
    "author": "IT-Projects LLC, Kolushov Alexandr",
    "support": "pos@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/12.0/vendor_extra_price/",
    "license": "Other OSI approved licence",  # MIT
    # "price": 9.00,
    # "currency": "EUR",
    "depends": ["purchase"],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/assets.xml",
        "views/pricelist.xml",
        "views/product.xml",
        "views/res_partner.xml",
    ],
    "qweb": [
        "static/src/xml/base_import.xml",
    ],
    "demo": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "auto_install": False,
    "installable": True,
}
