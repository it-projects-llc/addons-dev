# -*- coding: utf-8 -*-
from odoo import api, models, fields


class AccountCode(models.Model):
    _name = 'account.cr.d151.code'

    name = fields.Char(string='Code', required=True)
    description = fields.Char(string='Description', required=True)
    type = fields.Selection([('sale', 'Sale'), ('purchase', 'Purchase')], string='Type', required=True)
    category_ids = fields.One2many('account.cr.d151.category', 'code_id', string='Category')


class AccountCategory(models.Model):
    _name = 'account.cr.d151.category'

    name = fields.Char(string='Name', required=True)
    code_id = fields.Many2one('account.cr.d151.code', required=True)
    min_amount = fields.Float(string='Minimum amount')
    min_amount_currency_id = fields.Many2one('res.currency', required=True, string="Currency")
    sign = fields.Float(string='Sign In Report', digits=0)

    @api.constrains('sign')
    def _check_sign(self):
        for r in self:
            if int(r.sign) not in [1, -1]:
                raise ValueError('Sign In Report value should be 1 or -1.')


class Partner(models.Model):
    _inherit = 'res.partner'

    sale_cr_d151_category_id = fields.Many2one('account.cr.d151.category', 'Customer D151 category')
    purchase_cr_d151_category_id = fields.Many2one('account.cr.d151.category', 'Vendor D151 category')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_cr_d151_category_id = fields.Many2one('account.cr.d151.category', 'Customer D151 category')
    purchase_cr_d151_category_id = fields.Many2one('account.cr.d151.category', 'Vendor D151 category')


class ProductCategory(models.Model):
    _inherit = 'product.category'

    sale_cr_d151_category_id = fields.Many2one('account.cr.d151.category', 'Customer D151 category')
    purchase_cr_d151_category_id = fields.Many2one('account.cr.d151.category', 'Vendor D151 category')


class Account(models.Model):
    _inherit = 'account.account'

    sale_cr_d151_category_id = fields.Many2one('account.cr.d151.category', 'Customer D151 category')
    purchase_cr_d151_category_id = fields.Many2one('account.cr.d151.category', 'Vendor D151 category')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cr_d151_category_id = fields.Many2one('account.cr.d151.category', 'D151 category')

    @api.constrains('partner_id', 'cr_d151_category_id')
    def _check_partner(self):
        for r in self:
            if r.cr_d151_category_id and not r.partner_id:
                raise ValueError('Partner ID is required.')

    @api.onchange('partner_id', 'account_id')
    def _get_cr_151_category(self):
        if self.partner_id.sale_cr_d151_category_id:
            self.cr_d151_category_id = self.partner_id.sale_cr_d151_category_id

        elif self.partner_id.purchase_cr_d151_category_id:
            self.cr_d151_category_id = self.partner_id.purchase_cr_d151_category_id

        elif self.account_id.sale_cr_d151_category_id:
            self.cr_d151_category_id = self.account_id.sale_cr_d151_category_id

        elif self.account_id.purchase_cr_d151_category_id:
            self.cr_d151_category_id = self.account_id.purchase_cr_d151_category_id


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def invoice_line_move_line_get(self):
        res= []
        for line in self.invoice_line_ids:
            move_line = super(AccountInvoice, self).invoice_line_move_line_get()
            move_line = move_line[0]
            move_line['cr_d151_category_id'] = line.cr_d151_category_id.id
            res.append(move_line)
        return res

    def line_get_convert(self, line, part):
        res = super(AccountInvoice, self).line_get_convert(line, part)
        res['cr_d151_category_id'] = line.get('cr_d151_category_id', None)
        return res
            

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    cr_d151_category_id = fields.Many2one('account.cr.d151.category', 'D151 category')

    @api.onchange('cr_d151_category_id')
    def _compute_d151_domain(self):
        if self.invoice_id.type in ['in_invoice', 'in_refund']:
            domain = [('code_id.type', '=', 'purchase')]
        if self.invoice_id.type in ['out_invoice', 'out_refund']:
            domain = [('code_id.type','=' , 'sale')]
        return {
                'domain': {'cr_d151_category_id': domain},
        }

    @api.onchange('product_id', 'account_id', 'partner_id', 'invoice_id')
    def _get_cr_151_category(self):
        if self.invoice_id.type in ['in_invoice', 'in_refund']:

            parent_categ_d151 = self._get_parent_categ_d151(self.product_id.categ_id, in_flag=True)
            if self.product_id.purchase_cr_d151_category_id:
                self.cr_d151_category_id = self.product_id.purchase_cr_d151_category_id

            elif self.product_id.categ_id.purchase_cr_d151_category_id:
                self.cr_d151_category_id = self.product_id.categ_id.purchase_cr_d151_category_id

            elif parent_categ_d151:
                self.cr_d151_category_id = parent_categ_d151

            elif self.partner_id.purchase_cr_d151_category_id:
                self.cr_d151_category_id = self.partner_id.purchase_cr_d151_category_id

            elif self.account_id.purchase_cr_d151_category_id:
                self.cr_d151_category_id = self.account_id.purchase_cr_d151_category_id
        else:

            parent_categ_d151 = self._get_parent_categ_d151(self.product_id.categ_id)
            if self.product_id.sale_cr_d151_category_id:
                self.cr_d151_category_id = self.product_id.sale_cr_d151_category_id

            elif self.product_id.categ_id.sale_cr_d151_category_id:
                self.cr_d151_category_id = self.product_id.categ_id.sale_cr_d151_category_id

            elif parent_categ_d151:
                self.cr_d151_category_id = parent_categ_d151

            elif self.partner_id.sale_cr_d151_category_id:
                self.cr_d151_category_id = self.partner_id.sale_cr_d151_category_id

            elif self.account_id.sale_cr_d151_category_id:
                self.cr_d151_category_id = self.account_id.sale_cr_d151_category_id

    @classmethod
    def _get_parent_categ_d151(cls, categ_id, in_flag=False):
        if categ_id.parent_id:
            parent = categ_id.parent_id
            if not in_flag:
                if parent.sale_cr_d151_category_id:
                    return parent.sale_cr_d151_category_id
                else:
                    cls._get_parent_categ_d151(parent)
            else:
                if parent.purchase_cr_d151_category_id:
                    return parent.purchase_cr_d151_category_id
                else:
                    cls._get_parent_categ_d151(parent)
        return False


class AccountReconcileModel(models.Model):

    _inherit = 'account.reconcile.model'

    cr_d151_category_id = fields.Many2one('account.cr.d151.category', 'D151 category')
    second_cr_d151_category_id = fields.Many2one('account.cr.d151.category', 'D151 category')

    @api.onchange('account_id')
    def _get_cr_151_category(self):
        if self.account_id.sale_cr_d151_category_id:
            self.cr_d151_category_id = self.account_id.sale_cr_d151_category_id

        elif self.account_id.purchase_cr_d151_category_id:
            self.cr_d151_category_id = self.account_id.purchase_cr_d151_category_id

    @api.onchange('second_account_id')
    def _get_second_account_cr_151_category(self):
        if self.second_account_id.sale_cr_d151_category_id:
            self.second_cr_d151_category_id = self.second_account_id.sale_cr_d151_category_id

        elif self.second_account_id.purchase_cr_d151_category_id:
            self.second_cr_d151_category_id = self.second_account_id.purchase_cr_d151_category_id
