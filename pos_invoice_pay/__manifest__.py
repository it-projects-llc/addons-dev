# Copyright 2018 Artyom Losev
# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": """POS Invoice Pay""",
    "summary": """Paying invoiceable Sales Orders and confirmed Invoies over Point of Sale""",
    "category": "pos",
    "images": [],
    "version": "11.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Artyom Losev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "license": "LGPL-3",

    "depends": [
        "base_automation",
        "sale_management",
        "pos_longpolling",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "data.xml",
        "actions/base_action_rules.xml",
        "report/report.xml",
        "view.xml"
    ],
    "qweb": [
        'static/src/xml/pos.xml'
        ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
