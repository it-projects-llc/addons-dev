# -*- coding: utf-8 -*-
# Copyright 2019 Ilmir Karamov <https://it-projects.info/team/ilmir-k>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import odoo.tests


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_pos_dis_pay_rest(self):
        self.phantom_js(
            '/web',

            "odoo.__DEBUG__.services['web_tour.tour']"
            ".run('pos_order_print_check_tour')",

            "odoo.__DEBUG__.services['web_tour.tour']"
            ".tours.pos_order_print_check_tour.ready",

            login="admin",
            timeout=1000,
)
