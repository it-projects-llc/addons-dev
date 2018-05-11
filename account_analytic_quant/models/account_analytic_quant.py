# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
from odoo import models, fields, api


class AnalyticQuant(models.Model):
    _name = 'account.analytic.quant'

    type = fields.Selection([
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('expense_uncovered', 'Uncovered Expense'),
        ('expense_nonlinked', 'Nonlinked Expense'),
    ], string='Quant Type', help="""
* Uncovered Expense - is an expense that is not covereted by linked to it incomes
* Nonlinked Expense - is an expense that is not linked to any income
    """)
    profitability = fields.Selection([
        ('covered', 'Profitable'),
        ('oncovered', 'Unprofitable'),
    ], compute='_compute_profitability', store=True)
    amount = fields.Monetary('Amount')
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)

    income_id = fields.Many2one(
        'account.analytic.line',
        'Income',
        help="""The income this Quant is attached to.
        For income quant: reference to itself"""
    )
    income_project_id = fields.Many2one(
        'project.project',
        'Income Project',
        related='income_id.project_id',
        readonly=True,
    )

    line_id = fields.Many2one(
        'account.analytic.line',
        'Analytic Line'
    )
    task_id = fields.Many2one(
        'project.task',
        'Task',
        related='line_id.task_id',
        readonly=True,
    )
    project_id = fields.Many2one(
        'project.project',
        'Project',
        related='line_id.project_id',
        readonly=True,
    )

    @api.depends('type')
    def _compute_profitability(self):
        for r in self:
            r.profitability = 'covered' if r.type in ['income', 'expense'] \
                              else 'uncovered'
