# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    signature_image = fields.Binary(string='Signature')
    signature_added = fields.Boolean("Signature added?", default=False)

    @api.multi
    def action_invoice_open(self):
        if self.signature_added == True:
            # lots of duplicate calls to action_invoice_open, so we remove those already open
            to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
            if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft']):
                raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
            to_open_invoices.action_date_assign()
            to_open_invoices.action_move_create()
            return to_open_invoices.invoice_validate()
        else:
            raise UserError("Please, Get a signature from manager.")