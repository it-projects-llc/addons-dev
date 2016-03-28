from openerp import models, fields, api

from openerp.osv import fields as old_fields


class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    def _compute_quantity_max(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for id in ids:
            qty = 0
            line_ids = self.pool['account.invoice.line'].search(cr, uid, [('account_analytic_id', '=', id), ('invoice_id.state', '=', 'paid')])
            for line in self.pool['account.invoice.line'].browse(cr, uid, line_ids):
                attribute_value = line.product_id.attribute_value_ids.filtered(lambda r: r.attribute_id.code == 'sale_contract_hours.prepaid_service_units')
                if not attribute_value:
                    continue
                qty += float(attribute_value.code_value) * line.quantity

            res[id] = qty
        return res

    _columns = {
        'quantity_max': old_fields.function(_compute_quantity_max, string='Prepaid Service Units', help='')
    }
 
    unpaid_invoices_amount = fields.Float('Amount of unpaid invoices', compute='_compute_unpaid_invoices_amount')

    def _compute_unpaid_invoices_amount(self):
        for r in self:
            qty = 0
            for line in self.env['account.invoice.line'].search([('account_analytic_id', '=', r.id), ('invoice_id.state', 'not in', ['paid', 'draft', 'cancel'])]):
                qty += line.price_subtotal

            r.unpaid_invoices_amount = qty
