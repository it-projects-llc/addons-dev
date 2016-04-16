from openerp import models, fields, api

from openerp.osv import fields as old_fields


class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    def _compute_quantity_max(self, cr, uid, ids, fields, arg, context=None):
        res = dict([(i, {'quantity_max': 0, 'quantity_max_invoiced': 0, 'hours_quantity': 0}) for i in ids])
        for id in ids:
            domain = [('account_id', '=', id)]
            if context and context.get('contract_hours_start_date'):
                domain.append(('date', '<', context.get('contract_hours_start_date')))

            line_ids = self.pool['account.analytic.line'].search(cr, uid, domain)
            for line in self.pool['account.analytic.line'].browse(cr, uid, line_ids):
                if line.journal_id.type == 'general':
                    res[id]['hours_quantity'] += line.unit_amount
                    continue

                attribute_value = line.product_id.attribute_value_ids.filtered(lambda r: r.attribute_id.code == 'sale_contract_hours.prepaid_service_units')
                if not attribute_value:
                    continue
                res[id]['quantity_max_invoiced'] += line.unit_amount
                if line.invoice_id.state == 'paid':
                    res[id]['quantity_max'] += line.unit_amount
        return res

    _columns = {
        'quantity_max_invoiced': old_fields.function(_compute_quantity_max, string='Prepaid Service Units (Invoiced)', help='', multi='quantity_max'),
        'quantity_max': old_fields.function(_compute_quantity_max, string='Prepaid Service Units', help='', multi='quantity_max'),
        'hours_quantity': old_fields.function(_compute_quantity_max, multi='quantity_max', type='float', string='Total Worked Time',
            help="Number of time you spent on the analytic account (from timesheet). It computes quantities on all journal of type 'general'."),
    }
 
    unpaid_invoices_amount = fields.Float('Amount of unpaid invoices', compute='_compute_unpaid_invoices_amount')

    def _compute_unpaid_invoices_amount(self):
        for r in self:
            qty = 0
            for line in self.env['account.invoice.line'].search([('account_analytic_id', '=', r.id), ('invoice_id.state', 'not in', ['paid', 'draft', 'cancel'])]):
                qty += line.price_subtotal

            r.unpaid_invoices_amount = qty

    def generate_recurring_invoice(self):
        # TODO
        account = self.account_analytic_id
        partner = account.partner_id
        date_due = False
        if partner.property_payment_term:
            pterm_list = partner.property_payment_term.compute(value=1, date_ref=time.strftime('%Y-%m-%d'))
            if pterm_list:
                pterm_list = [l[0] for l in pterm_list]
                pterm_list.sort()
                date_due = pterm_list[-1]

        curr_invoice = {
            'name': time.strftime('%d/%m/%Y') + ' - '+account.name,
            'partner_id': account.partner_id.id,
            'company_id': account.company_id.id,
            'payment_term': partner.property_payment_term.id or False,
            'account_id': partner.property_account_receivable.id,
            'currency_id': account.pricelist_id.currency_id.id,
            'date_due': date_due,
            'fiscal_position': account.partner_id.property_account_position.id
        }
        return curr_invoice

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.line'

    unit_amount_invoicable = fields.Float('Invoicable Amount', compute='_compute_unit_amount_invoicable', store=True)

    @api.depends('unit_amount', 'to_invoice.factor')
    def _compute_unit_amount_invoicable(self):
        for r in self:
            r.unit_amount_invoicable = r.unit_amount * (100 - r.to_invoice.factor)/100.0

