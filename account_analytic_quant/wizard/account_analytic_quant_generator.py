# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
import logging
import datetime
import uuid


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
        'Generation Name',
        help='This name will be used for Generation filter'
    )

    def apply(self):
        self.ensure_one()

        Quant = self.env['account.analytic.quant'].sudo()
        generation = uuid.uuid4().hex
        generation_name = '%s #%s' % (self.name or 'Generation', generation[:5])
        _logger.info('Start quant generation: %s', generation_name)

        # New filter for Quants
        # remove previous default value
        self.env['ir.filters'].sudo().search([
            ('model_id', '=', 'account.analytic.quant'),
            ('is_default', '=', True),
            ('user_id', '=', False),
        ]).unlink()

        filter = self.env['ir.filters'].create({
            'name': generation_name,
            'is_default': True,
            'domain': "[('generation', '=', '%s')]" % generation,
            'model_id': 'account.analytic.quant',
            'action_id': self.env.ref('account_analytic_quant.analytic_quant_action').id,
        })
        filter.user_id = None

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
                 ('amount', '!=', 0),
                 ('id', 'not in', list(ready_expenses))])

        def _remaining(lines, quant_field, sign):
            res = dict([
                (line.id, line.amount)
                for line in lines
            ])
            quants = search_quants([
                ('type', '!=', 'income'),
                (quant_field, 'in', lines.ids)
            ])
            for q in quants:
                res[getattr(q, quant_field).id] += sign * q.amount

            return res

        def income_remaining(income_lines):
            return _remaining(income_lines, 'income_id', +1)

        def expense_remaining(expense_line):
            return _remaining(expense_line, 'line_id', -1)[expense_line.id]

        def expense_uncovered(line_expense):
            if line_expense.link_income_ids:
                return 'expense_uncovered'
            else:
                return 'expense_not_linked'

        # STAGE: Create quant for incomes
        _logger.info('Quant generation: Create quant for incomes')
        for line in search_lines([('is_expense', '=', False)]):
            # No need to split incomes
            amount = line.amount
            if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                continue
            Quant.create({
                'amount': amount,
                'type': 'income',
                # income is linked to itself
                'income_id': line.id,
                'line_id': line.id,
                'generation': generation,
            })

        # STAGE: linked
        _logger.info('Quant generation: distribute quants to corresponding incomes proportionally to link weight')
        for expense in search_expense_lines([
                ('link_income_ids', '!=', False)
        ]):
            total_weight = sum(
                expense.link_income_ids.mapped('weight')
            )
            available_income = income_remaining(
                expense.link_income_ids.mapped('income_id')
            )
            total_income = sum([a for id, a
                                in available_income.items()])

            if float_is_zero(total_income, precision_rounding=self.currency_id.rounding):
                # no space to distribute
                continue

            assert total_income > 0

            if abs(expense.amount) <= total_income:
                ready_expenses.add(expense.id)

            portion = min(abs(expense.amount), total_income) / total_weight

            for link_income in expense.link_income_ids:
                amount = portion * link_income.weight
                income = link_income.income_id
                amount = min(amount, available_income[income.id])
                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    continue
                Quant.create({
                    'amount': -1 * amount,
                    'type': 'expense',
                    'income_id': income.id,
                    'line_id': expense.id,
                    'generation': generation,
                })

        # Updates above might be heavy, so commit them to DB
        # self.env.cr.commit()

        # STAGE: destribute quants to incomes that belong to quants'
        # interval. Quants are distributed proportionally to size of found
        # incomes
        _logger.info('Quant generation: destribute quants to incomes that belong to quants interval. Quants are distributed proportionally to size of found incomes')
        for expense in search_expense_lines([]):
            # expense is negative!
            expense_amount = expense_remaining(expense)

            if float_is_zero(expense_amount, precision_rounding=self.currency_id.rounding):
                ready_expenses.add(expense.id)
                continue

            domain = [('is_expense', '=', False)]
            date_start = expense.date_start or expense.date
            date_end = expense.date_end or expense.date
            domain += [
                ('date_start', '<=', date_end),
                ('date_end', '>=', date_start)
            ]

            income_lines = search_lines(domain)

            if not income_lines:
                # no incomes in interval
                continue

            available_income = income_remaining(income_lines)
            for income in income_lines:
                delta = None
                if date(date_start) < date(income.date_start):
                    delta = date(date_end) - date(income.date_start)
                elif date_end > income.date_end:
                    delta = date(income.date_end) - date(date_start)
                else:
                    # expense is inside the income
                    continue
                # "1+" is needed. For example if date_start = date_end -- we
                # consider it as 1 day)
                income_days = 1 + (date(income.date_end) - date(income.date_start)).days
                intersection_days = 1 + delta.days
                assert income_days > 0
                assert intersection_days > 0

                available_income[income.id] *= intersection_days / income_days

            total_income = sum([a for id, a
                                in available_income.items()])

            if float_is_zero(total_income, precision_rounding=self.currency_id.rounding):
                # no space to distribute
                continue

            assert total_income > 0

            if abs(expense_amount) <= total_income:
                ready_expenses.add(expense.id)

            portion = min(abs(expense_amount), total_income) / total_income

            for income_id, income_amount in available_income.items():
                amount = -1 * portion * income_amount
                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    continue
                Quant.create({
                    'amount': amount,
                    'type': expense_uncovered(expense),
                    'income_id': income_id,
                    'line_id': expense.id,
                    'generation': generation,
                })

        # STAGE: distribute quants to income with closest date
        _logger.info('Quant generation: distribute quants to income with closest date')
        for expense in search_expense_lines([]):
            # expense is negative!
            expense_amount = expense_remaining(expense)

            if float_is_zero(expense_amount, precision_rounding=self.currency_id.rounding):
                ready_expenses.add(expense.id)
                continue

            select = 'id'
            order = ''
            where = 'is_expense=FALSE'
            select_params = []
            where_params = []
            date_start = expense.date_start or expense.date
            date_end = expense.date_end or expense.date
            # use undated income at the end
            select += ",CASE WHEN date_start IS NOT NULL AND date_end IS NOT NULL THEN least(date_start - %s, %s - date_end) ELSE interval '100333000 days' END AS days_delta"
            select_params.append(date_end)
            select_params.append(date_start)

            # only income outside of expenses are left -- so filter out other ones
            where += ' AND (date_start IS NULL OR date_end IS NULL OR date_start > %s OR %s > date_end)'
            where_params.append(date_end)
            where_params.append(date_start)

            order = 'ORDER BY days_delta'

            request = 'SELECT %s FROM account_analytic_line WHERE %s %s' % (select, where, order)
            request_params = [date(d) for d in select_params + where_params]
            self.env.cr.execute(request, request_params)
            ids = [row[0] for row in self._cr.fetchall()]

            income_lines = self.env['account.analytic.line'].browse(ids)

            if not income_lines:
                # no more incomes left
                _logger.info('No more incomes left to distriubute')
                break

            available_income = income_remaining(income_lines)

            total_income = sum([a for id, a
                                in available_income.items()])

            if float_is_zero(total_income, precision_rounding=self.currency_id.rounding):
                # no more incomes left
                _logger.info('Left incomes are distributed completly')
                break

            assert total_income > 0

            if abs(expense_amount) <= total_income:
                ready_expenses.add(expense.id)

            abs_expense_amount = abs(expense_amount)

            for income_id, income_amount in available_income.items():
                if float_is_zero(income_amount, precision_rounding=self.currency_id.rounding):
                    continue
                amount = -1 * min(abs_expense_amount, income_amount)
                Quant.create({
                    'amount': amount,
                    'type': expense_uncovered(expense),
                    'income_id': income_id,
                    'line_id': expense.id,
                    'generation': generation,
                })
                # amount is negative, so +=
                abs_expense_amount += amount

                if float_is_zero(abs_expense_amount, precision_rounding=self.currency_id.rounding):
                    break

        # FINAL STAGE: fill quant_income_id
        _logger.info('Quant generation: fill quant_income_id')
        for expense in search_quants([('type', '!=', 'income')]):
            if not expense.income_id:
                continue
            income = search_quants([('line_id', '=', expense.income_id.id)])
            expense.quant_income_id = income.id

        _logger.info('Quant generation: DONE!')
