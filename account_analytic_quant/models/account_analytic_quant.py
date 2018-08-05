# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
from odoo import models, fields, api


class AnalyticQuant(models.Model):
    _name = 'account.analytic.quant'

    generation = fields.Char('Generation', index=True)
    type = fields.Selection([
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('expense_uncovered', 'Uncovered Expense'),
        ('expense_not_linked', 'Not linked Expense'),
    ], string='Quant Type', index=True, help="""
* Uncovered Expense - is an expense that is not covereted by linked to it incomes
    """)
    profitability = fields.Selection([
        ('covered', 'Profitable'),
        ('uncovered', 'Unprofitable'),
    ], compute='_compute_profitability', store=True, index=True)
    amount = fields.Monetary('Amount')
    abs_amount = fields.Monetary(
        'Absolute Amount',
        compute='_compute_abs_amount',
        store=True,
        help="Makes Expense amount positive"
    )
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)

    # this cannot be related='quant_income_id.line_id', because for incomes we have:
    # * income_id is equal to line_id
    # * quant_income_id is False (otherwise the income appears in quant_expense_ids)
    income_id = fields.Many2one(
        'account.analytic.line',
        'Income',
        index=True,
        help="""The income this Quant is attached to.
        For income quant: reference to itself"""
    )
    income_account_id = fields.Many2one(
        'account.analytic.account',
        'Income Analytic',
        related='income_id.account_id',
        readonly=True,
        store=True,
        index=True,
    )

    quant_income_id = fields.Many2one(
        'account.analytic.quant'
    )
    quant_expense_ids = fields.One2many(
        'account.analytic.quant',
        'quant_income_id',
        help='Expenses attached to current income. Includes current the income too.',
    )

    line_id = fields.Many2one(
        'account.analytic.line',
        'Analytic Line',
        help='Original Analytic Line the quant is made from',
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        related='line_id.user_id',
        store=True,
        readonly=True,
    )
    date = fields.Date(
        'Date',
        related='line_id.date',
        store=True,
        readonly=True,
    )
    task_id = fields.Many2one(
        'project.task',
        'Task',
        related='line_id.task_id',
        store=True,
        readonly=True,
    )
    account_id = fields.Many2one(
        'account.analytic.account',
        'Analytic',
        related='line_id.account_id',
        store=True,
        readonly=True,
    )

    @api.depends('amount')
    def _compute_abs_amount(self):
        for r in self:
            r.abs_amount = abs(r.amount)

    @api.depends('type')
    def _compute_profitability(self):
        for r in self:
            if not r.type:
                continue
            r.profitability = 'covered' if r.type in ['income', 'expense'] \
                              else 'uncovered'
