# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
import logging

from odoo import models, fields, api


_logger = logging.getLogger(__name__)


class AnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    line_ids = fields.Many2many(
        'account.analytic.line',
        compute='_compute_line_ids',
        inverse='_inverse_line_ids',
        string='Linked Records',
    )
    is_expense = fields.Boolean(
        'Is Expense',
        store=True,
        compute='_compute_is_expense'
    )
    link_income_ids = fields.One2many(
        'account.analytic.line.link',
        'expense_id',
    )
    link_expense_ids = fields.One2many(
        'account.analytic.line.link',
        'income_id',
    )
    date_start = fields.Date('Start', help='Accumulation interval')
    date_end = fields.Date('End', help='Accumulation interval')

    @api.depends('amount')
    def _compute_is_expense(self):
        for r in self:
            r.is_expense = r.amount <= 0

    def _link_fields(self):
        self.ensure_one()
        field_this = 'expense_id' if self.is_expense else 'income_id'
        field_that = 'expense_id' if not self.is_expense else 'income_id'
        return field_this, field_that

    def _compute_line_ids(self):
        # It's not optimize to compute for multi recorset, because we show this
        # field in form only
        for this in self:
            field_this, field_that = this._link_fields()
            lines = self.env['account.analytic.line.link'].search(
                [(field_this, '=', this.id)]
            ).mapped(field_that)
            this.line_ids = lines

    def _inverse_line_ids(self):
        Link = self.env['account.analytic.line.link']
        for this in self:
            field_this, field_that = this._link_fields()

            existing = Link.search([
                (field_this, '=', this.id),
            ]).mapped(field_that)

            # create new
            for that in (this.line_ids - existing):
                Link.create({
                    field_this: this.id,
                    field_that: that.id,
                })

            # delete removed
            dangling = (existing - this.line_ids)
            links = Link.search([
                (field_this, '=', this.id),
                (field_that, 'in', dangling.ids),
            ])
            _logger.debug("Remove links: %s", links)
            links.unlink()
