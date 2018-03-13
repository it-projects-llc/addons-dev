# -*- coding: utf-8 -*-
import odoo.tests

# tests of other pos-modules are not compatible with the pos_menu module
# because some modules for tests use products
# We need use at_install = True only


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(False)
class TestUi(odoo.tests.HttpCase):

    def test_01_pos_is_loaded(self):
        self.phantom_js(
            '/web',

            "odoo.__DEBUG__.services['web_tour.tour']"
            ".run('pos_menu_tour')",

            "odoo.__DEBUG__.services['web_tour.tour']"
            ".tours.pos_menu_tour.ready",

            login="admin",
            timeout=240,
        )
