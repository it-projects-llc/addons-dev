# -*- coding: utf-8 -*-
# Copyright 2018 IT-Projects LLC <https://it-projects.info/> - All Rights Reserved.
# Unauthorized copying of this file, via any medium, is strictly prohibited.
# Proprietary and confidential.
# Written by Stanislav Krotov <https://www.it-projects.info/team/ufaks>, April 2018

import odoo.tests


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_01_odoo_backup_sh_tour(self):
        self.phantom_js('/', "odoo.__DEBUG__.services['web_tour.tour'].run('odoo_backup_sh_tour')",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours.odoo_backup_sh_tour.ready", login="admin")
