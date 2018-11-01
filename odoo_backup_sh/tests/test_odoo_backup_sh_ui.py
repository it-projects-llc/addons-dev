# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import requests_mock

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from odoo.api import Environment
from odoo.tests.common import HttpCase, at_install, post_install, HOST, PORT


@at_install(True)
@post_install(True)
class TestUi(HttpCase):

    def setUp(self):
        super(TestUi, self).setUp()

        self.fetch_dashboard_data_mock = requests_mock.Mocker(real_http=True)
        url = "http://%s:%s/odoo_backup_sh/fetch_dashboard_data" % (HOST, PORT)
        self.fetch_dashboard_data_mock.register_uri('GET', url, json={'configs': []})
        self.fetch_dashboard_data_mock.start()

        self.patcher_get_cloud_params = patch(
            'odoo.addons.odoo_backup_sh.controllers.main.BackupController.get_cloud_params',
            wraps=lambda *args: {})
        self.patcher_get_cloud_params.start()

        self.patcher_check_insufficient_credit = patch(
            'odoo.addons.odoo_backup_sh.controllers.main.BackupController.check_insufficient_credit',
            wraps=lambda *args: {'credit_url': 'https://iap.odoo.com/iap/1/credit...'})
        self.patcher_check_insufficient_credit.start()

    def test_odoo_backup_sh_tour(self):
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
        self.fetch_dashboard_data_mock.stop()
        self.patcher_get_cloud_params.stop()
        self.patcher_check_insufficient_credit.stop()
        super(TestUi, self).tearDown()
