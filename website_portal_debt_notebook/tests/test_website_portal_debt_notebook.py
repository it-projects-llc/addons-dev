# Copyright 2019 Anvar Kildebekov <https://it-projects.info/team/fedoranvar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import odoo.tests


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def common_test(self, test_login):

        env = self.env
        #  For QWeb-loading
        env['ir.module.module'].search([('name', '=', 'website_portal_debt_notebook')], limit=1).state = 'installed'
        #  Step 1:
        #  Set test-variables: partner_id, journal_id, currency_id
        balance = ["1.0",
                   "10.0"]
        now_date = ["01/01/2019 11:11:11",
                    "01/01/2019 22:22:22"]
        test_partner = env['res.users'].search([('login', '=', test_login)]).partner_id
        test_currency_id = env['res.currency'].search([('name', '=', 'USD')]).id
        #  Create journal
        test_journal = env['account.journal'].create({
            'name': "Test",
            'type': 'cash',
            'journal_user': True,
            'debt': True,
            'code': 'PLKS',
        })
        #  Create credit-records
        for i in range(2):
            env['pos.credit.update'].create({
                'partner_id': test_partner.id,
                'date': now_date[i],
                'journal_id': test_journal.id,
                'currency_id': test_currency_id,
                'balance': balance[i],
            }).switch_to_confirm()
        #  Step 2:
        #  run tour
        self.browser_js("/",
                        "odoo.__DEBUG__.services['web_tour.tour'].run('website_portal_debt_notebook_tour', 500)",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours.website_portal_debt_notebook_tour.ready",
                        login=test_login)

    def test_01_website_portal_debt_notebook(self):
        self.common_test("portal")
