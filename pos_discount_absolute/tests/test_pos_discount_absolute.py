
import odoo.tests
from odoo.api import Environment


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_pos_discounts(self):
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        cr = self.registry.cursor()
        env = Environment(cr, self.uid, {})
        env['ir.module.module'].search([('name', '=', 'pos_discount_absolute')], limit=1).state = 'installed'
        cr.release()

        # enable discounts in poses
        env['pos.config'].search([]).write({
            'module_pos_discount': True,
            'discount_abs_enabled': True,
        })

        self.phantom_js("/web",
                        "odoo.__DEBUG__.services['web_tour.tour'].run('pos_abs_discount_tour', 1000)",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours.pos_abs_discount_tour.ready",
                        login="admin")
