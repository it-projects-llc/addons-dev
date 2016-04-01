import time

from openerp import models, fields, api, exceptions


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    account_analytic_id = fields.Many2one('account.analytic.account',
                                          string='Contract')
    is_contract_hours_report = fields.Boolean('Contract Hours Report')
    contract_hours_start_date = fields.Date('Start date')
    contract_hours_end_date = fields.Date('End date')
    contract_hours_prepaid_product_id = fields.Many2one('product.product',
                                                string='Prepaid service Product')
    contract_hours_extra_product_id = fields.Many2one('product.product',
                                                string='Extra service Product')
    contract_hours_used = fields.Float('Total used hours in period', readonly=True)

    @api.multi
    def generate_contract_hours_report(self):
        for r in self:
            qty_prepaid_init = r.account_analytic_id.quantity_max
            qty_prepaid = qty_prepaid_init
            for line in self.evn['account.analytic.line'].search([
                    ('account_id', '=', r.id),
                    ('invoice_id', '=', False),
                    ('to_invoice', '!=', False),
                    ('date', '>=', r.contract_hours_start_date),
                    ('date', '<=', r.contract_hours_end_date),
            ]):
                line_qty_prepaid = 0
                if qty_prepaid > 0:
                    if qty_prepaid > line.unit_amount_invoicable:
                        line_qty_prepaid = line.unit_amount_invoicable
                    else:
                        line_qty_prepaid = qty_prepaid
                line_qty_extra = line.unit_amount_invoicable - line_qty_prepaid
                qty_prepaid -= line.unit_amount_invoicable

                if line_qty_prepaid:
                    r.create_line_work_hours_prepaid(line, line_qty_prepaid)
                if line_qty_extra:
                    r.create_line_work_hours_extra(line, line_qty_extra)

            r.contract_hours_used = qty_prepaid_init - qty_prepaid

    @api.multi
    def _line2name(self, line, product):
        self.ensure_one()
        return product.name

    @api.multi
    def _create_line(self, line, product):
        self.ensure_one()
        account = line.account_analytic_id
        pricelist = account.pricelist_id
        qty = line.unit_amount_invoicable
        unit_price = pricelist.price_get(product.id, qty, partner.id)
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
            'uos_id': uom,
            'account_analytic_id': account.id,
            'account_id': general_account.id,
        }
        return self.env['account.invoice.line'].create(curr_line)

    @api.multi
    def create_line_work_hours_prepaid(self, line, qty):
        self._create_line(line, self.contract_hours_prepaid_product_id)

    @api.multi
    def create_line_work_hours_extra(self, line, qty):
        self._create_line(line, self.contract_hours_extra_product_id)
