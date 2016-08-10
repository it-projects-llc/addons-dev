# -*- coding: utf-8 -*-
from openerp import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        res = super(AccountPayment, self)._onchange_payment_type()
        res['domain']['journal_id'].append(('id',
                                            'in', (self.env.user.branch_id.cash_journal_id.id,
                                                   self.env.user.branch_id.bank_journal_id.id)))
        return res


