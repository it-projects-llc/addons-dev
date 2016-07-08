# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import openerp.addons.decimal_precision as dp


class AccountMove(models.Model):
    _inherit = 'account.move'
    fleet_rental_document_id = fields.Many2one('fleet_rental.document_rent', readonly=True, copy=False)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    fleet_rental_document_id = fields.Many2one('fleet_rental.document_rent', readonly=True, copy=False)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fleet_rental_document_id = fields.Many2one('fleet_rental.document_rent', readonly=True, copy=False)

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        res = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
        fleet_rental_document_id = False
        for r in self.invoice_line_ids:
            if r.fleet_rental_document_id:
                fleet_rental_document_id = r.fleet_rental_document_id
                break
        if not fleet_rental_document_id:
            return res
        for move_line in move_lines:
            move_line[2]['fleet_rental_document_id'] = fleet_rental_document_id.id
        return move_lines

    @api.multi
    def register_payment(self, payment_line, writeoff_acc_id=False, writeoff_journal_id=False):
        try:
            payment_line.fleet_rental_document_id = self.fleet_rental_document_id
            self.partner_id.points += self.amount_untaxed
        except:
            pass
        res = super(AccountInvoice, self).register_payment(payment_line, writeoff_acc_id, writeoff_journal_id)

    @api.model
    def create(self, vals):
        invoice = super(AccountInvoice, self).create(vals)
        try:
            invoice.fleet_rental_document_id = vals['invoice_line_ids'][0][2]['fleet_rental_document_id']  # This needs for refunds.
        except:
            pass
        return invoice


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    fleet_rental_document_id = fields.Many2one('fleet_rental.document_rent', readonly=True, copy=False)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
        try:
            res = super(AccountPayment, self)._get_shared_move_line_vals(debit, credit, amount_currency, move_id, invoice_id)
            res['fleet_rental_document_id'] = self.invoice_ids[0].fleet_rental_document_id.id
        except:
            pass
        return res
