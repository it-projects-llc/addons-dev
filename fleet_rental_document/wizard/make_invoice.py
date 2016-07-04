# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError


class FleetRentalCreateInvoiceWizard(models.TransientModel):
    _name = "fleet_rental.create_invoice_wizard"

    amount = fields.Float('Down Payment Amount', digits=dp.get_precision('Account'), help="The amount to be invoiced in advance.")
    deposit_account_id = fields.Many2one("account.account", string="Income Account", domain=[('deprecated', '=', False)],\
        help="Account used for deposits")
    product_id = fields.Many2one('product.product', string='Down Payment Product', domain=[('type', '=', 'service')],\
        default=lambda self: self.env['ir.values'].get_default('sale.config.settings', 'deposit_product_id_setting'))
    advance_payment_method = fields.Selection([
        ('percentage', 'Down payment (percentage)'),
        ('fixed', 'Down payment (fixed amount)')
        ], string='What do you want to invoice?', default='fixed', required=True)

    @api.multi
    def _create_invoice(self, document, amount):
        inv_obj = self.env['account.invoice']

        account_id = False
        if self.product_id.id:
            account_id = self.product_id.property_account_income_id.id
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') % \
                    (self.product_id.name,))

        if self.amount <= 0.00:
            raise UserError(_('The value of the down payment amount must be positive.'))
        if self.advance_payment_method == 'percentage':
            amount = document.period_rent_price * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.amount
            name = _('Down Payment')

        invoice = inv_obj.create({
            'name': document.name,
            'origin': document.name,
            'fleet_rental_document_id': document.id,
            'type': 'out_invoice',
            'reference': False,
            'account_id': document.partner_id.property_account_receivable_id.id,
            'partner_id': document.partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': document.name,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': self.product_id.uom_id.id,
                'product_id': self.product_id.id,
                'fleet_rental_document_id': document.id,
            })],
        })
        return invoice

    @api.multi
    def create_invoices(self):
        documents = self.env['fleet_rental.document_rent'].browse(self._context.get('active_ids', []))

        # Create deposit product if necessary
        if not self.product_id:
            vals = self._prepare_deposit_product()
            self.product_id = self.env['product.product'].create(vals)
            self.env['ir.values'].sudo().set_default('sale.config.settings', 'deposit_product_id_setting', self.product_id.id)

        for document in documents:
            if self.advance_payment_method == 'percentage':
                amount = document.period_rent_price * self.amount / 100
            else:
                amount = self.amount
            if self.product_id.type != 'service':
                raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))

            self._create_invoice(document, amount)

        if self._context.get('open_invoices', False):
            return documents.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    def _prepare_deposit_product(self):
        return {
            'name': 'Down payment',
            'type': 'service',
            'invoice_policy': 'order',
            'property_account_income_id': self.deposit_account_id.id,
        }
