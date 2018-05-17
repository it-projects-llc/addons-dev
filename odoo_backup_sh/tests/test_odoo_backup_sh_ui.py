# -*- coding: utf-8 -*-
# Copyright 2018 IT-Projects LLC <https://it-projects.info/> - All Rights Reserved.
# Unauthorized copying of this file, via any medium, is strictly prohibited.
# Proprietary and confidential.
# Written by Stanislav Krotov <https://www.it-projects.info/team/ufaks>, April 2018

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

        def patch_load_backup_list_from_service(redirect=None):
            return {'backup_list': ['01.01.2018 - backup1', '02.01.2018 - backup2']}
            # TODO: check a case with rendering list of backups in dashboard

        def patch_check_insufficient_credit(credit):
            return 'https://iap.odoo.com/iap/1/credit...'

        self.patcher1 = patch(
            'odoo.addons.odoo_backup_sh.controllers.main.BackupController.load_backup_list_from_service',
            wraps=patch_load_backup_list_from_service)
        self.patcher2 = patch(
            'odoo.addons.odoo_backup_sh.models.odoo_backup_sh.Backup.check_insufficient_credit',
            wraps=patch_check_insufficient_credit)
        self.patcher1.start()
        self.patcher2.start()

    def test_01_odoo_backup_sh_tour(self):
        self.phantom_js("/web", "odoo.__DEBUG__.services['web_tour.tour'].run('odoo_backup_sh_tour')",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours.odoo_backup_sh_tour.ready", login="admin")

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        super(TestUi, self).tearDown()
