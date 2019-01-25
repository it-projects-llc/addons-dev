{
    "name": """City Total Limit""",
    "summary": """City Total Limit""",
    "category": "Base",
    "images": [],
    "version": "12.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "support": "pos@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/12.0/res_city_total_limit/",
    "license": "LGPL-3",
    # "price": 0.00,
    # "currency": "EUR",

    "depends": [
        "base_automation",
        "base_address_city",
        "website_sale",
        "contacts"
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/res_city_total_limit_view.xml",
        "views/website_sale_template.xml",
        "data/data.xml",
    ],
    "qweb": [],
    "demo": [],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
