# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError


class FleetBookingCreateBillWizard(models.TransientModel):
    _name = "fleet_booking.create_bill_wizard"

    @api.model
    def _default_amount(self):
        return self.env['fleet.vehicle'].browse(self._context.get('active_id')).car_value


    amount = fields.Float('Payment Amount', digits=dp.get_precision('Account'),
                          help="The amount to be invoiced.",
                          default=_default_amount)

    @api.multi
    def _create_invoice(self, document, amount):
        self.ensure_one()
        inv_obj = self.env['account.invoice']

        account_id = False
        if document.product_id.id:
            account_id = document.product_id.property_account_expense_id.id
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                (document.product_id.name,))

        if self.amount <= 0.00:
            raise UserError(_('The value of the payment amount must be positive.'))

        amount = self.amount

        if not document.analytic_account_id:
            document.document_id.analytic_account_id = self.env['account.analytic.account'].sudo().create({'name': document.name + '_' + document.create_date, 'partner_id': document.partner_id.id}).id

        invoice = inv_obj.create({
            'type': 'in_invoice',
            'reference': False,
            'account_id': document.partner_id.property_account_payable_id.id,
            'partner_id': document.partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': document.product_id.name,
                'origin': document.name,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': document.product_id.uom_id.id,
                'product_id': document.product_id.id,
                'fleet_rental_document_id': document.document_id.id,
                'account_analytic_id': document.document_id.analytic_account_id.id,
            })],
        })
        if document.asset_id:
            document.asset_id.invoice_id = invoice
        return invoice

    @api.multi
    def create_invoices(self):
        documents = self.env[self._context.get('active_model')].browse(self._context.get('active_ids', []))
        document = self.env[self._context.get('active_model')].browse(self._context.get('active_id', []))

        # Create product if necessary
        if not document.product_id:
            document.product_id = self._create_product(document)

        # Create asset if necessary
        if not document.asset_id and document.account_asset_id and document.account_depreciation_id:
            document.asset_id = self._create_asset(document)

        # Create vendor if necessary
        if not document.partner_id:
            document.partner_id = self._create_partner(document)

        for document in documents:
            amount = self.amount
            self._create_invoice(document, amount)

        if self._context.get('open_invoices', False):
            return documents.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    def _create_product(self, document):
        vals = {
            'name': document.name,
            'type': 'service',
            'invoice_policy': 'order',
        }
        product = self.env['product.product'].create(vals)
        return product

    def _create_partner(self, document):
        vals = {
            'name': document.name + ' Vehicle Vendor',
            'supplier': True,
            'customer': False,
            'type': 'contact',
        }
        partner = self.env['res.partner'].create(vals)
        return partner

    def _create_asset(self, document):
        vals = {
            'name': 'Asset category for ' + document.name,
            'account_asset_id': document.account_asset_id.id,
            'account_depreciation_id': document.account_depreciation_id.id,
            'journal_id': self.env['account.journal'].search([('code', '=', 'MISC')])[0].id,
            'type': 'purchase',
        }
        asset_category = self.env['account.asset.category'].create(vals)
        vals = {
            'name': 'Asset ' + document.name,
            'value': document.car_value,
            'category_id': asset_category.id,
        }
        asset = self.env['account.asset.asset'].create(vals)
        return asset
