import time

from openerp import models, fields, api, exceptions, _


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    def _default_prepaid_product_id(self):
        return self.env.ref('sale_contract_hours.product_prepaid_hours',
                            raise_if_not_found=False).id

    account_analytic_id = fields.Many2one('account.analytic.account',
                                          string='Contract')
    is_contract_hours_report = fields.Boolean('Contract Hours Report')
    contract_hours_start_date = fields.Date('Start date')
    contract_hours_end_date = fields.Date('End date')
    contract_hours_prepaid_product_id = \
        fields.Many2one('product.product', string='Prepaid service Product',
                        help='Zero-priced product for lines with prepaid service',
                        default=_default_prepaid_product_id,
                    )
    contract_hours_extra_product_id = fields.Many2one('product.product',
                                                string='Extra service Product')
    contract_hours_used = fields.Float('Total used hours in period', readonly=True)

    @api.multi
    def generate_contract_hours_report(self):
        for r in self:
            # clean previous lines
            r.write({'invoice_line': [(5, 0, 0)]})
            self.env['account.analytic.line'].search([('invoice_id', '=', r.id)]).write({'invoice_id': False})

            qty_prepaid_init = r.with_context(contract_hours_start_date=r.contract_hours_start_date).account_analytic_id.remaining_hours
            qty_prepaid = qty_prepaid_init
            contract_hours_used = 0
            for line in self.env['account.analytic.line'].search([
                    ('account_id', '=', r.account_analytic_id.id),
                    ('to_invoice', '!=', False),
                    ('date', '>=', r.contract_hours_start_date),
                    ('date', '<=', r.contract_hours_end_date),
            ], order="date"):
                if line.journal_id.type == 'sale':
                    qty_prepaid += line.unit_amount
                    continue
                elif line.invoice_id and line.invoice_id.state != 'cancel':
                    # line is already invoiced
                    continue
                line_qty_prepaid = 0
                if qty_prepaid > 0:
                    if qty_prepaid > line.unit_amount_invoicable:
                        line_qty_prepaid = line.unit_amount_invoicable
                    else:
                        line_qty_prepaid = qty_prepaid

                contract_hours_used += line.unit_amount_invoicable

                line_qty_extra = line.unit_amount_invoicable - line_qty_prepaid
                qty_prepaid -= line.unit_amount_invoicable

                if line_qty_prepaid:
                    r.create_line_work_hours_prepaid(line, line_qty_prepaid)
                if line_qty_extra:
                    r.create_line_work_hours_extra(line, line_qty_extra)

            r.contract_hours_used = contract_hours_used

    @api.multi
    def _line2name(self, line, product):
        self.ensure_one()
        return product.name

    @api.multi
    def _create_line(self, line, product, qty):
        self.ensure_one()
        account = self.account_analytic_id
        partner = self.partner_id
        pricelist = account.pricelist_id
        unit_price = pricelist.price_get(product.id, qty, partner.id)[pricelist.id]
        name = self._line2name(line, product)
        uom = line.product_uom_id
        general_account = product.property_account_income or product.categ_id.property_account_income_categ
        if not general_account:
            raise exceptions.Warning(_("Configuration Error!"), _("Please define income account for product '%s'.") % product.name)

        curr_line = {
            'price_unit': unit_price,
            'quantity': qty,
            'product_id': product.id or False,
            'invoice_id': self.id,
            'name': name,
            'uos_id': uom.id,
            'account_analytic_id': account.id,
            'account_id': general_account.id,
        }
        return self.env['account.invoice.line'].create(curr_line)

    @api.multi
    def create_line_work_hours_prepaid(self, line, qty):
        self._create_line(line, self.contract_hours_prepaid_product_id, qty)

    @api.multi
    def create_line_work_hours_extra(self, line, qty):
        self._create_line(line, self.contract_hours_extra_product_id, qty)
