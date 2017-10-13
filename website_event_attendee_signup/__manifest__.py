# -*- coding: utf-8 -*-
{
    "name": """Sign-up event attendees to portal""",
    "summary": """Attendees can use portal dashboard to make extra purchases for the event, for example.""",
    "category": "Marketing",
    # "live_test_url": "",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/yelizariev",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "{DEPENDENCY1}",
        "{DEPENDENCY2}",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "{FILE1}.xml",
        "{FILE2}.xml",
    ],
    "qweb": [
        "static/src/xml/{QWEBFILE1}.xml",
    ],
    "demo": [
        "demo/{DEMOFILE1}.xml",
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
