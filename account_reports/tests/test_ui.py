# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo.tests


@odoo.tests.tagged('post_install','-at_install')
class TestUi(odoo.tests.HttpCase):
    def test_ui(self):
        self.phantom_js("/web", "odoo.__DEBUG__.services['web_tour.tour'].run('account_followup_reports_widgets')", "odoo.__DEBUG__.services['web_tour.tour'].tours.account_followup_reports_widgets.ready", login='admin')
