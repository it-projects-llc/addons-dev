# -*- coding: utf-8 -*-
{
    "name": """Attendee registration: Birthdate, Passport, Nationality""",
    "summary": """Ask information on registration and stores at Partner record""",
    "category": "Marketing",
    # "live_test_url": "",
    "images": ['static/description/custom-fields-750.png'],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/yelizariev",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "website_event_attendee_fields",
        "partner_contact_birthdate",
        "partner_firstname",
        "partner_identification",
        "partner_contact_nationality",
        "website_event_sale",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "data/event_event_attendee_field_data.xml",
        "views/website_event_templates.xml",
    ],
    "qweb": [
    ],
    "demo": [
        "data/event_event_demo.yml",
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
