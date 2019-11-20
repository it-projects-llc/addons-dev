# Copyright 2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import odoo.tests


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_open_pos(self):
        # without a delay there might be problems on the steps whilst opening a POS
        # caused by a not yet loaded button's action
        env = self.env
        env['ir.module.module'].search([('name', '=', 'pos_durak')], limit=1).state = 'installed'

        self.phantom_js("/web",
                        "odoo.__DEBUG__.services['web_tour.tour'].run('tour_pos_durak')",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours.tour_pos_durak.ready",
                        login="admin", timeout=80)
