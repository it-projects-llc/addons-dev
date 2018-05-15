# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
import logging

from odoo import models, fields, api
from odoo.tools import float_is_zero


_logger = logging.getLogger(__name__)


class Generator(models.TransientModel):
    _name = 'account.analytic.quant.generator'

    quant_amount = fields.Monetary(
        'Quant size',
        required=True,
    )
    date = fields.Date(
        'Starting Date',
    )
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)

    def apply(self):
        self.ensure_one()
        _logger.debug('Start quant generation')

        Quant = self.env['account.analytic.quant']
        generation = Quant.search(limit=1, order='generation desc').generation or 0

        def search_quants(extra_domain):
            return Quant.search(
                [('generation', '=', generation)] + extra_domain
            )

        line_domain = []
        if self.date:
            line_domain += [('date', '>=', self.date)]

        ready_expenses = set()

        def search_lines(extra_domain):
            return self.env['account.analytic.line'].search(
                line_domain + extra_domain,
                order='date asc')

        def search_expense_lines(extra_domain):
            return search_lines(
                extra_domain +
                [('is_expense', '=', True),
                 ('id', 'not in', list(ready_expenses))])


        def _remaining(lines, quant_field, sign):
            res = dict([
                (line.id, line.amount)
                for line in lines
            ])
            quants = search_quants([
                (quant_field, 'in', lines.ids)
            ])
            for q in quants:
                res[q.id] += sign * q.amount

            return res

        def income_remaining(income_lines):
            return _remaining(income_lines, 'income_id', +1)

        def expense_remaining(expense_line):
            return _remaining(expense_line, 'line_id', -1)[expense_line.id]

        # STAGE: Create quant for incomes
        for line in search_lines([('is_expense', '=', False)]):
            # No need to split incomes
            Quant.create({
                'amount': line.amount,
                'type': 'income',
                # income is linked to itself
                'income_id': line.id,
                'line_id': line.id,
                'generation': generation,
            })

        # STAGE distribute quants to corresponding incomes proportionally to
        # link weight
        for expense in search_expense_lines([
                ('line_id.link_income_ids', '!=', False)
        ]):
            total_weight = sum(
                expense.link_income_ids.mapped('weight')
            )
            available_income = income_remaining(
                expense.link_income_ids.mapped('income_id')
            )
            total_income = sum([amount for id, amount
                                in available_income.items()])

            if float_is_zero(total_income):
                # no space to distribute
                continue

            assert total_income > 0

            if abs(expense.amount) <= total_income:
                ready_expenses.add(expense.id)

            portion = min(abs(expense.amount), total_income) / total_weight

            for link_income in expense.link_income_ids:
                Quant.create({
                    'amount': -1 * portion * link_income.weight,
                    'type': 'expense',
                    'income_id': link_income.income_id.id,
                    'line_id': expense.id,
                    'generation': generation,
                })

        # Updates above might be heavy, so commit them to DB
        # self.env.cr.commit()

        # STAGE: destribute quants to incomes that belong to quants'
        # interval. Quants are distributed proportionally to size of found
        # incomes
        for expense in search_expense_lines([]):
            # expense is negative!
            expense_amount = expense_remaining(expense)

            if float_is_zero(expense):
                ready_expenses.add(expense.id)

            domain = [('is_expense', '=', False)]
            if expense.date_start and expense.date_end:
                domain += [
                    ('date_start', '<', expense.date_end)
                    ('date_end', '>', expense.date_start)
                ]

            income_lines = search_lines(domain)

            if not income_lines:
                # no incomes in interval
                continue

            available_income = income_remaining(income_lines)
            for income in income_lines:
                delta = None
                if expense.date_start < income.date_start:
                    delta = expense.date_end - income.date_start
                elif expense.date_end > income.date_end:
                    delta = expense.date_start - income.date_end
                else:
                    # expense is inside the income
                    continue
                # "1+" is needed. For example if date_start = date_end -- we
                # consider it as 1 day)
                income_days = 1 + (income.date_start - income.date_end).days
                intersection_days = 1 + delta.days
                available_income[income.id] *= intersection_days / income_days

            total_income = sum([amount for id, amount
                                in available_income.items()])

            if float_is_zero(total_income):
                # no space to distribute
                continue

            assert total_income > 0

            if abs(expense_amount) <= total_income:
                ready_expenses.add(expense.id)

            portion = min(abs(expense_amount), total_income) / total_income

            for income_id, income_amount in available_income.items():
                Quant.create({
                    'amount': -1 * portion * income_amount,
                    'type': 'expense_uncovered',
                    'income_id': income_id,
                    'line_id': expense.id,
                    'generation': generation,
                })


        # STAGE: distribute quants to income with closest date
        for expense in search_expense_lines([]):
            # expense is negative!
            expense_amount = expense_remaining(expense)

            if float_is_zero(expense):
                ready_expenses.add(expense.id)

            select = 'id'
            order = ''
            where = 'is_expense=FALSE'
            select_params = []
            where_params = []
            if expense.date_start and expense.date_end:
                # use undated income at the end
                select += ',IF date_start AND date_end THEN least(date_start - %s, %s - date_end) ELSE 100333000 as days_delta;'
                select_params.append(expense.date_end)
                select_params.append(expense.date_start)

                # only income outside of expenses are left -- so filter out other ones
                where += 'AND (date_start > %s OR %s > date_end)'
                where_params.append(expense.date_end)
                where_params.append(expense.date_start)

                order = 'ORDER BY days_delta'

            request = '%s FROM account_analytic_line WHERE %s %s' % (select, where, order)
            self.env.cr.execute(request, select_params + where_params)
            ids = [row['id'] for row in self._cr.fetchall()]

            income_lines = self.env['account.analytic.line'].browse(ids)

            if not income_lines:
                # no more incomes left
                break

            available_income = income_remaining(income_lines)

            total_income = sum([amount for id, amount
                                in available_income.items()])

            if float_is_zero(total_income):
                # no more incomes left
                break

            assert total_income > 0

            if abs(expense_amount) <= total_income:
                ready_expenses.add(expense.id)

            portion = min(abs(expense_amount), total_income) / total_income

            for income_id, income_amount in available_income.items():
                Quant.create({
                    'amount': -1 * portion * income_amount,
                    'type': 'expense_uncovered',
                    'income_id': income_id,
                    'line_id': expense.id,
                    'generation': generation,
                })

