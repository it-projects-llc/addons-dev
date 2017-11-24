# -*- coding: utf-8 -*-
import odoo.tests


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_01_pos_is_loaded(self):
        self.phantom_js(
            '/pos/web?m=1',

            "odoo.__DEBUG__.services['web_tour.tour']"
            ".run('pos_order_merge_tour')",

            "odoo.__DEBUG__.services['web_tour.tour']"
            ".tours.pos_order_merge_tour.ready",

            login="admin",
            timeout=240,
        )
