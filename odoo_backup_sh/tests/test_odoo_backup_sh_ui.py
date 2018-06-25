# -*- coding: utf-8 -*-
# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.api import Environment
import odoo.tests
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def setUp(self):
        super(TestUi, self).setUp()

        def patch_update_info(redirect=None):
            return {
                'backup_list': ['database_1|2018-06-20_10-44-43', 'database_2|2018-06-20_10-47-13'],
                'credit_url': 'https://iap.odoo.com/iap/1/credit...',
            }

        self.patcher1 = patch(
            'odoo.addons.odoo_backup_sh.controllers.main.BackupController.update_info',
            wraps=patch_update_info)
        self.patcher1.start()

    def test_01_odoo_backup_sh_tour(self):
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        cr = self.registry.cursor()
        assert cr == self.registry.test_cr
        env = Environment(cr, self.uid, {})
        env['ir.module.module'].search([('name', '=', 'odoo_backup_sh')], limit=1).state = 'installed'
        cr.release()
        self.phantom_js("/web", "odoo.__DEBUG__.services['web_tour.tour'].run('odoo_backup_sh_tour')",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours.odoo_backup_sh_tour.ready", login="admin")

    def tearDown(self):
        self.patcher1.stop()
        super(TestUi, self).tearDown()
