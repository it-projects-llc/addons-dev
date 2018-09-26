# Copyright 2017-2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": """POS Absolute and Relative Discounts""",
    "summary": """Provides absolute discounting for Point of Sale""",
    "category": "Point of Sale",
    "version": "11.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Kolushov Alexandr",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "license": "LGPL-3",

    "depends": [
        "pos_discount_base",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views.xml',
    ],
    'qweb': [
        'static/src/xml/DiscountAbs.xml',
    ],
    "demo": [
        "demo/demo.xml",
    ],

    "auto_install": False,
    "installable": True,
}
