import odoo.tests
from odoo.api import Environment


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_01_pos_change_price_after_click_button(self):
        # see more https://odoo-development.readthedocs.io/en/latest/dev/tests/js.html#phantom-js-python-tests
        env = Environment(self.registry.test_cr, self.uid, {})

        # create new pricelist
        pricelist = env['product.pricelist'].create({
            'name': 'POS pricelist',
            'pos_discount_policy': 'without_discount',
        })

        env['product.pricelist.item'].create({
            'pricelist_id': pricelist.id,
            'compute_price': 'percentage',
            'percent_price': 10,
            'applied_on': '3_global',
        })

        all_pricelists = env['product.pricelist'].search([('currency_id', '=', env.user.company_id.currency_id.id)])

        # get exist pos_config
        main_pos_config = env.ref('point_of_sale.pos_config_main')

        main_pos_config.write({
            'use_pricelist': True,
            'available_pricelist_ids': [(4, p.id) for p in all_pricelists],
            'pricelist_id': pricelist.id,
            'show_orderline_default_pricelist': True,
        })

        # create new session and open it
        main_pos_config.open_session_cb()

        # From https://github.com/odoo/odoo/blob/11.0/addons/point_of_sale/tests/test_frontend.py#L292-L297
        #
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        env['ir.module.module'].search([('name', '=', 'pos_pricelist_custom')], limit=1).state = 'installed'

        self.phantom_js(
            '/pos/web',

            "odoo.__DEBUG__.services['web_tour.tour']"
            ".run('pos_pricelist_custom_tour')",

            "odoo.__DEBUG__.services['web_tour.tour']"
            ".tours.pos_pricelist_custom_tour.ready",

            login="admin",
        )
