# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import odoo.tests
from odoo.api import Environment


# parseXML is undefined in tests "TypeError: undefined is not an object (evaluating 'template.children[0]')\n"
@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(False)
class TestUi(odoo.tests.HttpCase):

    def test_pos_receipt(self):
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        cr = self.registry.cursor()
        env = Environment(cr, self.uid, {})
        env['ir.module.module'].search([('name', '=', 'pos_receipt_custom')], limit=1).state = 'installed'
        cr.release()

        # enable custom tickets in poses
        env['pos.config'].search([]).write({
            'custom_ticket': True,
            'custom_ticket_id': self.env.ref('pos_receipt_custom.simple_pos_ticket').id,
        })

        self.phantom_js("/web",
                        "odoo.__DEBUG__.services['web_tour.tour'].run('pos_receipt_custom_tour', 1000)",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours.pos_receipt_custom_tour.ready",
                        login="admin")
