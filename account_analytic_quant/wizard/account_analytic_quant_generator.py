# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
import logging
import datetime


from odoo import models, fields
from odoo.tools import float_is_zero
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


_logger = logging.getLogger(__name__)


def date(s):
    return datetime.datetime.strptime(s, DATE_FORMAT)


class Generator(models.TransientModel):
    _name = 'account.analytic.quant.generator'

    quant_amount = fields.Monetary(
        'Quant size',
        required=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id.id,
    )
    date = fields.Date(
       'Starting Date',
    )
    name = fields.Char(
        'Name',
        help='This name will be used for Generation filter'
    )

    def apply(self):
        self.ensure_one()

        Quant = self.env['account.analytic.quant']
        generation = Quant.search([], limit=1, order='generation desc').generation or 0
        generation += 1
        _logger.debug('Start quant generation %s', generation)

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
                res[getattr(q, quant_field).id] += sign * q.amount

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
                ('link_income_ids', '!=', False)
        ]):
            total_weight = sum(
                expense.link_income_ids.mapped('weight')
            )
            available_income = income_remaining(
                expense.link_income_ids.mapped('income_id')
            )
            total_income = sum([amount for id, amount
                                in available_income.items()])

            if float_is_zero(total_income, precision_rounding=self.currency_id.rounding):
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

            if float_is_zero(expense_amount, precision_rounding=self.currency_id.rounding):
                ready_expenses.add(expense.id)

            domain = [('is_expense', '=', False)]
            if expense.date_start and expense.date_end:
                domain += [
                    ('date_start', '<', expense.date_end),
                    ('date_end', '>', expense.date_start)
                ]

            income_lines = search_lines(domain)

            if not income_lines:
                # no incomes in interval
                continue

            available_income = income_remaining(income_lines)
            if expense.date_start and expense.date_end:
                for income in income_lines:
                    delta = None
                    if date(expense.date_start) < date(income.date_start):
                        delta = date(expense.date_end) - date(income.date_start)
                    elif expense.date_end > income.date_end:
                        delta = date(income.date_end) - date(expense.date_start)
                    else:
                        # expense is inside the income
                        continue
                    # "1+" is needed. For example if date_start = date_end -- we
                    # consider it as 1 day)
                    income_days = 1 + (date(income.date_end) - date(income.date_start)).days
                    intersection_days = 1 + delta.days

                    available_income[income.id] *= intersection_days / income_days

            total_income = sum([amount for id, amount
                                in available_income.items()])

            if float_is_zero(total_income, precision_rounding=self.currency_id.rounding):
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

            if float_is_zero(expense_amount, precision_rounding=self.currency_id.rounding):
                ready_expenses.add(expense.id)

            select = 'id'
            order = ''
            where = 'is_expense=FALSE'
            select_params = []
            where_params = []
            if expense.date_start and expense.date_end:
                # use undated income at the end
                select += ",CASE WHEN date_start IS NOT NULL AND date_end IS NOT NULL THEN least(date_start - %s, %s - date_end) ELSE interval '100333000 days' END AS days_delta"
                select_params.append(expense.date_end)
                select_params.append(expense.date_start)

                # only income outside of expenses are left -- so filter out other ones
                where += ' AND (date_start > %s OR %s > date_end)'
                where_params.append(expense.date_end)
                where_params.append(expense.date_start)

                order = 'ORDER BY days_delta'

            request = 'SELECT %s FROM account_analytic_line WHERE %s %s' % (select, where, order)
            request_params = [date(d) for d in select_params + where_params]
            self.env.cr.execute(request, request_params)
            ids = [row[0] for row in self._cr.fetchall()]

            income_lines = self.env['account.analytic.line'].browse(ids)

            if not income_lines:
                # no more incomes left
                break

            available_income = income_remaining(income_lines)

            total_income = sum([amount for id, amount
                                in available_income.items()])

            if float_is_zero(total_income, precision_rounding=self.currency_id.rounding):
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

