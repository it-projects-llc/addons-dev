# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    partner_type = fields.Selection(selection_add=[("seller", "Seller")])

    @api.one
    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id')
    def _compute_payment_difference(self):
        if len(self.invoice_ids) == 0:
            return
        self.payment_difference = self._compute_payment_amount() - self.amount
        if self._context.get("active_model", False) == "seller.payment":
            self.payment_difference = abs(self.env["seller.payment"].browse(
                self._context["active_id"]).payable_amount) - self.amount

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands(
            'invoice_ids', rec.get('invoice_ids'))
        ctx = self._context.copy()
        if ctx.get("active_model", False) == "seller.payment":
            seller_payment_obj = self.env[
                "seller.payment"].browse(ctx["active_id"])
            rec["invoice_ids"] = [(5,), (4, seller_payment_obj.invoice_id.id)]
            rec["partner_type"] = "seller"
            rec["communication"] = seller_payment_obj.name
            rec["amount"] = abs(seller_payment_obj.payable_amount)
            rec["payment_type"] = "outbound"
            rec["partner_id"] = seller_payment_obj.seller_id.id
        return rec

    @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
                A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
                and another in the destination reconciliable account (see _compute_destination_account_id).
                If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
                If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:

            if rec.state != 'draft':
                raise UserError(
                    _("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(
                    _("The payment cannot be processed because the invoice is not open!"))

            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence = rec.env.ref('account.sequence_payment_transfer')
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence = rec.env.ref(
                            'account.sequence_payment_customer_invoice')
                    if rec.payment_type == 'outbound':
                        sequence = rec.env.ref(
                            'account.sequence_payment_customer_refund')
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence = rec.env.ref(
                            'account.sequence_payment_supplier_refund')
                    if rec.payment_type == 'outbound':
                        sequence = rec.env.ref(
                            'account.sequence_payment_supplier_invoice')
                if rec.partner_type == 'seller':
                    if rec.payment_type == 'inbound':
                        sequence = rec.env.ref(
                            'odoo_marketplace.sequence_payment_seller_refund')
                    if rec.payment_type == 'outbound':
                        sequence = rec.env.ref(
                            'odoo_marketplace.sequence_payment_seller_invoice')
            rec.name = sequence.with_context(
                ir_sequence_date=rec.payment_date).next_by_id()

            # Create the journal entry
            amount = rec.amount * \
                (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and
            # credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(
                    lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.state = 'posted'
