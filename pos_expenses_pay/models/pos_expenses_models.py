# Copyright 2018 Artyom Losev
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
from werkzeug import url_encode

CHANNEL = "pos_expenses"


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pay_expenses = fields.Boolean("Pay Expenses", help="Show Expenses in POS", default=True)

    @api.model
    def notify_expenses_updates(self, ids):
        message = {"updated_expenses": [ids]}
        self.search([])._send_to_channel(CHANNEL, message)


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    processed_by_pos = fields.Boolean()
    cashier = fields.Char()
    payment_datetime = fields.Datetime(required=True, string="Datetime")

    def process_expense_from_pos(self, cashier):
        if (self.state == 'approve'):
            self.action_sheet_move_create()
        vals = self.get_vals_for_payment(cashier)
        self.cashier = cashier
        payment = self.env['account.payment'].create(vals)
        payment.post()

        body = (_("A payment of %s %s with the reference <a href='/mail/view?%s'>%s</a> related to your expense %s has been made by %s in POS.") % (payment.amount, payment.currency_id.symbol, url_encode({'model': 'account.payment', 'res_id': payment.id}), payment.name, self.name, cashier))
        self.message_post(body=body)

        # Reconcile the payment and the expense, i.e. lookup on the payable account move lines
        account_move_lines_to_reconcile = self.env['account.move.line']
        for line in payment.move_line_ids + self.account_move_id.line_ids:
            if line.account_id.internal_type == 'payable':
                account_move_lines_to_reconcile |= line
        account_move_lines_to_reconcile.reconcile()
        self.processed_by_pos = True
        return self.id

    def get_vals_for_payment(self, cashier):
        partner_id = self.address_id.id or self.employee_id.id and self.employee_id.address_home_id.id
        date = fields.Date.context_today(self)
        # Cash method as default
        payment_method_id = 2
        journal_id = 8
        return {
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'partner_id': partner_id,
            'journal_id': journal_id,
            'company_id': self.company_id.id,
            'payment_method_id': payment_method_id,
            'amount': self.total_amount,
            'currency_id': self.currency_id.id,
            'payment_date': date,
            'communication': cashier,
        }

    def action_updated_expense(self):
        self.env['pos.config'].notify_expenses_updates(self.id)

    @api.multi
    def set_to_paid(self):
        super(HrExpenseSheet, self).set_to_paid()
        self.write({
            'payment_datetime': fields.Datetime.now(),
        })
