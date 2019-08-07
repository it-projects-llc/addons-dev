{
    "name": """Website Team""",
    "summary": """Team""",
    "category": "website",
    # "live_test_URL": "",
    "images": ["images/website_team.png"],
    "version": "12.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Kolushov Alexandr",
    "support": "apps@it-projects.info",
    # "website": "https://it-projects.info",
    "license": "LGPL-3",
    # "price": 0.00,
    # "currency": "EUR",

    "depends": [
        "website",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/website_team_template.xml",
        "views/website_team_view.xml",
    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
