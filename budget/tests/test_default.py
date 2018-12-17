import logging
from openerp.tests.common import HttpCase
from odoo.fields import Date
import datetime


class TestBudget(HttpCase):

    at_install = True
    post_install = True

    def setUp(self):
        super(TestBudget, self).setUp()

        group_budget_responsible = self.env.ref('budget.group_budget_responsible')
        group_account_manager = self.env.ref('account.group_account_manager')

        # Create a first user to run the tests in this module
        self.env['res.users'].create({
            'name': 'Aurore',
            'login': 'aurore',
            'password': 'aurore',
            'groups_id': [(6, 0, [group_budget_responsible.id])]
        })

        # Create a second user to run the tests in this module
        self.env['res.users'].create({
            'name': 'Beth',
            'login': 'beth',
            'password': 'beth',
            'groups_id': [(6, 0, [group_budget_responsible.id, group_account_manager.id])]
        })

        tag_ids = self.env.ref('account.account_tag_operating')

        self.general_account = self.env['account.account'].create({
            'name': 'Expenses - (test)',
            'code': 'X2120',
            'user_type_id': self.env.ref('account.data_account_type_expenses').id,
            'tag_ids': [(6, 0, [tag_ids.id])]
        })

        # Auth by Aurore
        self.authenticate('aurore', 'aurore')

        # Create new Budget Item
        self.budget_item_1 = self.env["budget.item"].create({
            "name": "Budget item 1",
            "code": "BI1",
            "account": [(6, 0, [self.general_account.id])]
        })

    def test_active_version(self):
        # Select for this file a user that is not admin
        self.authenticate('beth', 'beth')

        # Create a new budget
        budget = self.env['budget.budget'].create({
            "name": "January Budget",
            "start_date": "2013-01-01",
            "stop_date": "2013-01-31",
            "budget_item_id": self.budget_item_1.id
        })

        # Create a new version
        version_1 = self.env['budget.version'].create({
            "name": "Version 1",
            "budget_id": budget.id,
            "currency_id": self.env.ref('base.EUR').id
        })

        # Budget Version should not be active
        self.assertFalse(version_1.is_active, "Budget Version should be is not active")

        # Press the button to make it active
        version_1.make_active()

        # Budget Version should be active now
        self.assertTrue(version_1.is_active, "Budget Version should be is active")

        # Create now a second version
        version_2 = self.env['budget.version'].create({
            "name": "Version 2",
            "budget_id": budget.id,
            "currency_id": self.env.ref('base.EUR').id
        })

        # Only the first one should be active
        self.assertTrue(version_1.is_active, "First Budget Version should be is active")
        self.assertFalse(version_2.is_active, "Second Budget Version should be is not active")

        # Press the button to make it active
        version_2.make_active()

        # Only the second one should now be active
        self.assertFalse(version_1.is_active, "First Budget Version should be is not active")
        self.assertTrue(version_2.is_active, "Second Budget Version should be is active")

        # The active version of the budget should be the second one
        self.assertEqual(budget.active_version_id.id, version_2.id, "The active version should be the second one")

    def test_analytic_amount_and_duplicate_budget(self):

        # Select for this file a user that is not admin
        self.authenticate('aurore', 'aurore')

        # Create a new budget
        budget = self.env['budget.budget'].create({
            "name": "Budget test",
            "start_date": Date.from_string('%s-01-01' % (datetime.datetime.now().year + 1)),
            "stop_date": Date.from_string('%s-12-31' % (datetime.datetime.now().year + 1)),
            "budget_item_id": self.budget_item_1.id
        })

        # Create a new version
        version_1 = self.env['budget.version'].create({
            "name": "Version 1",
            "budget_id": budget.id,
            "currency_id": self.env.ref('base.USD').id
        })

        # Create a budget line
        line = self.env["budget.line"].create({
            "analytic_account_id": self.env.ref("analytic.analytic_agrolait").id,
            "budget_item_id": self.budget_item_1.id,
            "amount": -200.0,
            "currency_id": self.env.ref('base.USD').id,
            "budget_version_id": version_1.id
        })

        # Assert that the real amount and the diff amount are correct
        res = abs(line.analytic_amount + 200.0) < 1e-4
        self.assertTrue(res, "Analytic amount is not correct! -200.0 != %s" % line.analytic_amount)
        res = abs(line.analytic_real_amount - 0.0) < 1e-4
        self.assertTrue(res, "Analytic real amount is not correct! -200.0 != %s" % line.analytic_real_amount)
        res = abs(line.analytic_diff_amount - 200.0) < 1e-4
        self.assertTrue(res, "Analytic diff amount is not correct! -200.0 != %s" % line.analytic_diff_amount)

        company = self.env.ref('base.main_company')
        company.create_op_move_if_non_existant()
        move_line = self.env['account.move.line'].with_context({'check_move_validity': False}).create({
            'name': 'Test line 1',
            'move_id': company.account_opening_move_id.id,
            'account_id': self.general_account.id,
            'company_id': company.id,
            'amount_currency': 10.0,
            'currency_id': self.env.ref('base.USD').id,
        })

        # Create an account analytic line
        self.env['account.analytic.line'].create({
            'account_id': self.env.ref("analytic.analytic_agrolait").id,
            'move_id': move_line.id,
            'name': 'Line to test budget line'
        })

        # Assert that the real amount and the diff amount are correct
        res = abs(line.analytic_amount + 200.0) < 1e-4
        self.assertTrue(res, "Analytic amount is not correct! -200.0 != %s" % line.analytic_amount)
        res = abs(line.analytic_real_amount - 10.0) < 1e-4
        self.assertTrue(res, "Analytic real amount is not correct! -200.0 != %s" % line.analytic_real_amount)
        res = abs(line.analytic_diff_amount - 210.0) < 1e-4
        self.assertTrue(res, "Analytic diff amount is not correct! -200.0 != %s" % line.analytic_diff_amount)

        # Select for this file a user that is not admin
        self.authenticate('beth', 'beth')

        # The version we start with should have one line
        self.assertTrue(len(version_1.budget_line_ids) == 1, "The version should have one line")

        # Make it active
        version_1.make_active()

        # After duplicate it, the new version should don't have lines
        copy_version_1 = version_1.copy()
        self.assertTrue(len(copy_version_1.budget_line_ids) == 0, "The new version should don't have lines")

        # The old version should be inactive now
        self.assertFalse(version_1.is_active, "Budget Version should be is not active")

    def test_default_end_date(self):

        # Select for this file a user that is not admin
        self.authenticate('beth', 'beth')

        # Create a new budget
        budget = self.env['budget.budget'].create({
            "name": "Budget Test March",
            "start_date": "2013-03-05",
            "budget_item_id": self.budget_item_1.id
        })

        budget._onchange_start_stop_date()

        # The end date should be filled automatically at the end of the same month
        self.assertTrue(budget.stop_date == "2013-03-31", "Stop date is not correct! '2013-03-31' != %s" % budget.stop_date)

        # Create another budget starting on April
        budget_2 = self.env['budget.budget'].create({
            "name": "Budget Test April",
            "start_date": "2013-04-10",
            "budget_item_id": self.budget_item_1.id
        })

        budget_2._onchange_start_stop_date()

        # The end date should be on the 30th
        self.assertTrue(budget_2.stop_date == "2013-04-30", "Stop date is not correct! '2013-04-30' != %s" % budget_2.stop_date)
