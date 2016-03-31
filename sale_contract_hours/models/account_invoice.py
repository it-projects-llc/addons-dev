from openerp import models, fields, api

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    account_analytic_id = fields.Many2one('account.analytic.account', string='Contract')
    is_contract_hours_report = fields.Boolean('Contract hours report')
    contract_hours_start_date = fields.Date('Start date')
    contract_hours_end_date = fields.Date('End date')

    @api.multi
    def generate_contract_hours_report(self):
        for r in self:
            qty = r.quantity_max
            for line in self.evn['account.analytic.line'].search([('to_invoice', '!=', False), ('account_id', '=', r.id), ('invoice_id', '=', false), ('date', '>=', r.contract_hours_start_date), ('date', '<=', r.contract_hours_end_date)]):
                pass
