# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": """Income-Expense Analysis""",
    "summary": """Split incomes in quants and distribute them among expenses""",
    "category": "Accounting",
    # "live_test_url": "",
    "images": [],
    "version": "10.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/yelizariev",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "analytic",
        "hr_timesheet",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/account_analytic_line.xml",
    ],
    "demo": [
        "demo/res.users.csv",
        "demo/account.analytic.account.csv",
        "demo/project.project.csv",
        "demo/project.task.csv",
        "demo/account.analytic.line.csv",
#        "demo/account.analytic.line.link.csv",
    ],
    "qweb": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,
}
