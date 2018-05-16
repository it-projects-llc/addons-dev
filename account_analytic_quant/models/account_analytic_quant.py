# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
from odoo import models, fields, api


class AnalyticQuant(models.Model):
    _name = 'account.analytic.quant'

    generation = fields.Integer('Generation', index=True)
    type = fields.Selection([
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('expense_uncovered', 'Uncovered Expense'),
    ], string='Quant Type', index=True, help="""
* Uncovered Expense - is an expense that is not covereted by linked to it incomes
    """)
    profitability = fields.Selection([
        ('covered', 'Profitable'),
        ('uncovered', 'Unprofitable'),
    ], compute='_compute_profitability', store=True, index=True)
    amount = fields.Monetary('Amount')
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)

    income_id = fields.Many2one(
        'account.analytic.line',
        'Income',
        index=True,
        help="""The income this Quant is attached to.
        For income quant: reference to itself"""
    )
    income_project_id = fields.Many2one(
        'project.project',
        'Income Project',
        related='income_id.project_id',
        readonly=True,
        index=True,
    )

    line_id = fields.Many2one(
        'account.analytic.line',
        'Analytic Line',
        help='Original Analytic Line the quant is made from',
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
            if not r.type:
                continue
            r.profitability = 'covered' if r.type in ['income', 'expense'] \
                              else 'uncovered'
