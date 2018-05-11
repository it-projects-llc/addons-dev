# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
from odoo import models, fields


class AnalyticLink(models.Model):
    _name = 'account.analytic.line.link'

    income_id = fields.Many2one('account.analytic.line', 'Income')
    expense_id = fields.Many2one('account.analytic.line', 'Expense')
    weight = fields.Integer('Weight', default=1)

    def name_get(self):
        return [
            (r.id, '%s <> %s' % (r.income_id.name, r.expense_id.name))
            for r in self
        ]
