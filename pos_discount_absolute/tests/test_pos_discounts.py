# -*- coding: utf-8 -*-

import odoo.tests


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_pos_discounts(self):
        self.phantom_js("/web", "odoo.__DEBUG__.services['web_tour.tour'].run('pos_discount_tour')",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours.pos_discount_tour.ready",
                        login="admin")
