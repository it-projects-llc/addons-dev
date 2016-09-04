# -*- coding: utf-8 -*-
from openerp import api, fields, models


class FleetBranch(models.Model):
    _name = "fleet_branch.branch"
    _inherit = 'mail.thread'

    name = fields.Char('Branch Name', required=True)
    city = fields.Char(string='City')
    phone = fields.Char(string='Phone')
    branch_target = fields.Char(string='Branch Target')
    branch_officer_ids = fields.One2many('res.users', 'branch_id',
                                         string="Branch Officers", readonly=True)
    state = fields.Selection([('new', 'New'),
                              ('active', 'Active')],
                             string='State', default='new')

    deposit_account_id = fields.Many2one("account.account", string="Advanced Deposit Account",
                                         domain=[('deprecated', '=', False)],
                                         help="Account used for deposits", required=True)
    rental_account_id = fields.Many2one("account.account", string="Sales Account",
                                        domain=[('deprecated', '=', False)],
                                        help="Account used for rental sales", required=True)
    deposit_product_id = fields.Many2one('product.product', 'Deposit Product',
                                         domain="[('type', '=', 'service')]")
    rental_product_id = fields.Many2one('product.product', 'Rental Product',
                                        domain="[('type', '=', 'service')]")
    cash_account_id = fields.Many2one("account.account", string="Cash Account",
                                      domain=[('deprecated', '=', False)],
                                      required=True)
    bank_account_id = fields.Many2one("account.account", string="Bank Account",
                                      domain=[('deprecated', '=', False)],
                                      required=True, track_visibility='onchange')
    cash_journal_id = fields.Many2one('account.journal',
                                      domain=[('type', 'in', ('cash'))])
    bank_journal_id = fields.Many2one('account.journal',
                                      domain=[('type', 'in', ('bank'))])
    vehicle_ids = fields.One2many('fleet.vehicle', 'branch_id')


    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'bank_account_id' in init_values:
            return 'fleet_branch.mt_test_branch'
        return super(FleetBranch, self)._track_subtype(init_values)

    @api.model
    def create(self, vals):
        # Create a default branch cash/bank journals
        name = vals.get('name')
        cash_account_id = vals.get('cash_account_id')
        bank_account_id = vals.get('bank_account_id')
        vals['cash_journal_id'] = self.env['account.journal'].create({
            'name': 'Cash',
            'code': self.env['ir.sequence'].next_by_code('account.journal_cash'),
            'type': 'cash',
            'default_credit_account_id': cash_account_id,
            'default_debit_account_id': cash_account_id,
        }).id
        vals['bank_journal_id'] = self.env['account.journal'].create({
            'name': 'Bank',
            'code': self.env['ir.sequence'].next_by_code('account.journal_bank'),
            'type': 'bank',
            'default_credit_account_id': bank_account_id,
            'default_debit_account_id': bank_account_id,
        }).id

        return super(FleetBranch, self).create(vals)
