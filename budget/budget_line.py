##############################################################################
#
#    Author: Arnaud Wüst
#    Copyright 2009-2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DTF
from datetime import datetime


class BudgetLine(models.Model):

    """ Budget line.

    A budget version line NOT linked to an analytic account """

    _name = "budget.line"
    _description = "Budget Lines"
    _order = 'name ASC'

    @api.depends('currency_id', 'budget_currency_id', 'amount')
    def _compute_budget_currency_amount(self):
        """ line's amount xchanged in the budget's currency """
        for r in self:
            if r.budget_currency_id and r.amount:
                r.budget_amount = r.currency_id.compute(r.amount, r.budget_currency_id)

    @api.depends('currency_id', 'analytic_account_id.line_ids', 'amount')
    def _compute_analytic_amount(self):
        """ Compute the amounts in the analytic account's currency """
        anl_lines_obj = self.env['account.analytic.line']
        for line in self:
            anl_account = line.analytic_account_id
            if not anl_account:
                continue

            anl_currency_id = line.analytic_currency_id

            amount = line.currency_id.compute(line.amount, anl_currency_id)
            fnl_account_ids = [acc.id for acc in line.budget_item_id.all_account_ids]

            # real amount is the total of analytic lines
            # within the time frame, we'll read it in the
            # analytic account's currency, as for the
            # the budget line so we can compare them

            domain = [('general_account_id', 'in', fnl_account_ids), ('account_id', '=', anl_account.id)]

            if line.start_date:
                domain.append(('date', '>=', line.start_date))
            if line.stop_date:
                domain.append(('date', '<=', line.stop_date))

            anl_lines = anl_lines_obj.search(domain)
            real = sum([l.currency_id.compute(l.analytic_amount_currency, anl_currency_id) for l in anl_lines])

            line.analytic_amount = amount
            line.analytic_real_amount = real
            line.analytic_diff_amount = real - amount

    def _get_budget_version_currency(self):
        """ return the default currency for this line of account.
        The default currency is the currency set for the budget
        version if it exists """
        if self.env.context.get('currency_id'):
            return self.env['res.currency'].browse(self.env.context['currency_id'])

    def _fetch_budget_line_from_aal(self):
        """
        return the list of budget line to which belong the
        analytic.account.line `ids´
        """
        account_ids = []
        for aal in self:
            if aal.account_id and aal.account_id.id not in account_ids:
                account_ids.append(aal.account_id.id)
        return self.browse(account_ids)

    start_date = fields.Date('Start Date')
    stop_date = fields.Date('End Date')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    budget_item_id = fields.Many2one('budget.item', string='Budget Item', required=True, ondelete='restrict')
    allocation = fields.Char(related='budget_item_id.allocation_id.name', string='Budget Item Allocation',
                             readonly=True)
    name = fields.Char(string='Description')
    amount = fields.Float(string='Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=_get_budget_version_currency)
    budget_amount = fields.Float(compute='_compute_budget_currency_amount', string="In Budget's Currency",
                                 digits=dp.get_precision('Account'), store=True)
    budget_currency_id = fields.Many2one(related='budget_version_id.currency_id', string='Budget Currency',
                                         readonly=True)
    budget_version_id = fields.Many2one('budget.version', string='Budget Version', required=True, ondelete='cascade')
    analytic_amount = fields.Float(compute='_compute_analytic_amount', digits=dp.get_precision('Account'),
                                   multi='analytic', string="In Analytic Amount's Currency")
    analytic_real_amount = fields.Float(compute='_compute_analytic_amount', digits=dp.get_precision('Account'),
                                        multi='analytic', string="Analytic Real Amount")
    analytic_diff_amount = fields.Float(compute='_compute_analytic_amount', digits=dp.get_precision('Account'),
                                        multi='analytic', string="Analytic Difference Amount")
    analytic_currency_id = fields.Many2one(related='analytic_account_id.currency_id', string='Analytic Currency',
                                           readonly=True)

    @api.onchange('start_date', 'stop_date')
    def _onchange_start_stop_date(self):
        def date_valid(date, budget):
            if not date:
                return True
            else:
                date = datetime.strptime(date, DTF)
            return date >= datetime.strptime(budget.start_date, DTF) and date <= datetime.strptime(budget.stop_date, DTF)

        if self.stop_date and not self.start_date:
            self.stop_date = False
            return {
                'warning': {
                    'title': _("Error"),
                    'message': _("The end date must be after the start date"),
                }
            }

        if self.start_date and not self.budget_version_id:
            self.start_date = False
            return {
                'warning': {
                    'title': _("Error"),
                    'message': _("Please specify Budget Version first"),
                }
            }

        res = date_valid(self.start_date, self.budget_version_id.budget_id) and date_valid(self.stop_date, self.budget_version_id.budget_id)
        if res is not True:
            self.stop_date = False
            return {
                'warning': {
                    'title': _("Error"),
                    'message': _("The line's dates must be within the budget's start and end dates"),
                }
            }

    def init(self):
        def migrate_period(period_column, date_column):
            cr = self.env.cr
            sql = ("SELECT column_name FROM information_schema.columns "
                   "WHERE table_name = 'budget_line' "
                   "AND column_name = %s")
            cr.execute(sql, (period_column, ))
            if not cr.fetchall():
                return

            sql = ("UPDATE budget_line "
                   "SET {1} = (SELECT {1} FROM account_period "
                   "           WHERE account_period.id = budget_line.{0}) "
                   ", {0} = NULL "
                   "WHERE {1} IS NULL "
                   "AND {0} IS NOT NULL"
                   ).format(period_column, date_column)
            cr.execute(sql)

        migrate_period('period_id', 'start_date')
        migrate_period('to_period_id', 'stop_date')

    @api.onchange('analytic_account_id')
    def onchange_analytic_account_id(self):
        self.currency_id = self.analytic_account_id.currency_id.id
