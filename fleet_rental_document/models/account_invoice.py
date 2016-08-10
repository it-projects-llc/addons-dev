# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    fleet_rental_document_id = fields.Many2one('fleet_rental.document', readonly=True, copy=False)

