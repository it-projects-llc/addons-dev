# -*- coding: utf-8 -*-
from openerp.exceptions import UserError
from openerp import fields, models, api, _
import openerp.addons.decimal_precision as dp


class InstallmentType(models.Model):
    _name = 'fleet_booking.installment_type'

    name = fields.Char('Installment type')
    product_id = fields.Many2one('product.product')


class InstallmentDate(models.Model):
    _name = 'fleet_booking.installment_date'
    _order = 'installment_date'

    @api.model
    def _default_type(self):
        if self._context.get('default_type_ref', False):
            return self.env.ref(self._context.get('default_type_ref')).id

    vehicle_id = fields.Many2one('fleet.vehicle', required=True)
    installment_date = fields.Date('Date', required=True)
    amount = fields.Float(string='Amount', digits_compute=dp.get_precision('Product Price'),
                          default=0, required=True)
    bill_id = fields.Many2one('account.invoice')
    bill_check = fields.Boolean(compute='_get_bill_check', string='Posted', store=True)
    type_id = fields.Many2one('fleet_booking.installment_type', default=_default_type)
    partner_id = fields.Many2one('res.partner', string='Vendor')

    @api.multi
    def _get_bill_product(self):
        """
        :returns: a product to be used in bills
        """
        self.ensure_one()
        return self.type_id.product_id

    @api.one
    @api.depends('bill_id')
    def _get_bill_check(self):
        self.bill_check = bool(self.bill_id)

    @api.multi
    def _make_bill(self):
        for record in self:
            account_id = False
            product = record._get_bill_product()

            account_id = product.property_account_expense_id.id

            if not account_id:
                raise UserError(
                    _('There is no expense account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                    (product.name,))

            # Create vendor if necessary
            if not record.partner_id:
                record.partner_id = record._get_partner()

            invoice = self.env['account.invoice'].create({
                'type': 'in_invoice',
                'reference': False,
                'account_id': record.partner_id.property_account_payable_id.id,
                'partner_id': record.partner_id.id,
                'invoice_line_ids': [(0, 0, {
                    'name': product.name,
                    'origin': record.vehicle_id.name,
                    'account_id': account_id,
                    'price_unit': record.amount,
                    'quantity': 1.0,
                    'discount': 0.0,
                    'uom_id': record.type_id.product_id.uom_id.id,
                    'product_id': record.type_id.product_id.id,
                })],
            })

            record.bill_id = invoice

    def _get_partner(self):
        self.ensure_one()
        vals = {
            'name': self.type_id.name + ' ' + self.vehicle_id.name,
            'supplier': True,
            'customer': False,
            'type': 'contact',
        }
        if self.type_id == self.env.ref('fleet_booking.installment_type_lease'):
            if not self.vehicle_id.lease_partner_id:
                self.vehicle_id.lease_partner_id = self.env['res.partner'].create(vals)
            return self.vehicle_id.lease_partner_id
        if self.type_id == self.env.ref('fleet_booking.installment_type_insurance'):
            if not self.vehicle_id.insurance_partner_id:
                self.vehicle_id.insurance_partner_id = self.env['res.partner'].create(vals)
            return self.vehicle_id.insurance_partner_id
