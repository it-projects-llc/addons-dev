# coding: utf-8
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": """Website Sale Customisation""",
    "summary": """{SHORT_DESCRIPTION_OF_THE_MODULE}""",
    "category": "{MODULE_CATEGORY}",
    # "live_test_url": "",
    "images": [],
    "version": "10.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, ",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/KolushovAlexandr",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "website_sale_checkout_store",
        "document",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/views.xml",
        "views/partner_form.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": "country_updates",
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,
}
