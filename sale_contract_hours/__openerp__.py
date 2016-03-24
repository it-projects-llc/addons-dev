# -*- coding: utf-8 -*-
{
    "name": """Hours-based service sales""",
    "summary": """Extra features for Sale Contracts""",
    "category": "Sales Management",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Ivan Yelizariev",
    "website": "https://it-projects.info",
    "license": "GPL-3",
    #"price": 9.00,
    #"currency": "EUR",

    "depends": [
        "sale",
        "account_analytic_analysis",
        "product_price_factor",
        "product_attribute_code",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
    ],
    "demo": [
        'demo/product_demo.xml'
    ],
    "installable": True,
    "auto_install": False,
}
