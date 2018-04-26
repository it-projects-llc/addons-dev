# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class PurchaseOrderWizard(models.TransientModel):
    _name = 'purchase.order.wizard'
    _description = 'Generate Purchase Order from Sale Order'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True, change_default=True)
    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')
    date_order = fields.Datetime('Order Date', index=True, copy=False, default=fields.Datetime.now,
                                 help="Depicts the date where the Quotation should be validated and converted into a purchase order.")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id.id)
    order_line_ids = fields.One2many('purchase.order.line.wizard', 'order_id', string='Order Lines', copy=True)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True,
                                    help="Not empty if an origin for purchase order was sale order")

    def create_purchase_orders(self):
        warning = self.check_vendors()
        if warning:
            raise ValidationError(warning)

        po_env = self.env['purchase.order']
        vendor_ids = map(lambda x: x.partner_id.id, self.order_line_ids)
        for ven in vendor_ids:

            so_lines = self.order_line_ids.filtered(lambda l: l.partner_id.id == ven and l.product_qty_to_order > 0)
            if not len(so_lines):
                continue

            p_order = po_env.search([('partner_id', '=', ven),
                                     ('customer_id', '=', self.partner_id.id),
                                     ('sale_order_id', '=', self.sale_order_id.id)])
            if len(p_order):
                p_order = p_order[0]
                p_order.write({
                    'date_order': self.date_order,
                    'currency_id': self.currency_id.id,
                    'order_line': [(5, 0, 0)],
                })
            else:
                p_order = po_env.create({
                    'name': self.env['ir.sequence'].next_by_code('purchase.order') or '/',
                    'date_order': self.date_order,
                    'partner_id': ven,
                    'currency_id': self.currency_id.id,
                    'sale_order_id': self.sale_order_id.id,
                    'customer_id': self.partner_id.id,
                    'order_line': False,
                })

            for line in so_lines:
                o_line = self.env['purchase.order.line'].create({
                    'name': line.name,
                    'product_qty': line.product_qty_to_order,
                    'date_planned': line.date_planned,
                    'order_id': p_order.id,
                    'product_uom': line.product_uom.id,
                    'product_id': line.product_id.id,
                    'price_unit': line.purchase_price,
                    'taxes_id': [(6, 0, line.taxes_id.ids)],
                })
                p_order.write({
                    'order_line': [(4, o_line.id)]
                })

    def check_vendors(self):
        message = ''
        for line in self.order_line_ids:
            if line.product_qty_to_order > 0 and not line.partner_id:
                message = message + 'Define a Vendor for the line with product "' + line.product_id.name + '"\n'
        if message:
            message = 'Vendor is not defined \n' + message
        return message

    def create_po_lines_from_so(self, s_order):
        for line in s_order.order_line:
            product = self.env['product.product'].browse(line.product_id.id)
            mto_id = self.env['stock.location.route'].search([('name', 'like', _('Make To Order'))], limit=1).id
            mto_product = mto_id in product.product_tmpl_id.route_ids.ids
            supplier_id = False
            product_qty_to_order = max(line.product_uom_qty - max(product.virtual_available, 0), 0)
            vendors = product.product_tmpl_id.seller_ids.filtered(
                lambda s: s.min_qty <= product_qty_to_order and self.check_date_availability(s))
            seller_ids = False
            purchase_price = product.standard_price
            if len(vendors):
                supplier_id = vendors[0].id
                purchase_price = vendors[0].price
                seller_ids = [(6, 0, vendors.ids)]
            taxes = product.product_tmpl_id.supplier_taxes_id
            taxes = taxes and [(6, 0, taxes.ids)] or False
            p_line = self.env['purchase.order.line.wizard'].create({
                'name': line.name,
                'product_qty_sold': line.product_uom_qty,
                'product_qty_to_order': product_qty_to_order,
                'product_uom': line.product_uom.id,
                'product_id': product.id,
                'order_id': self.id,
                'supplier_id': supplier_id,
                'purchase_price': purchase_price,
                'mto_product': mto_product,
                'taxes_id': taxes,
                'seller_ids': seller_ids,
            })
            self.order_line_ids += p_line

    def check_date_availability(self, vendor):
        return (not vendor.date_end or self.date_order <= vendor.date_end) and \
                (not vendor.date_start or vendor.date_start <= self.date_order)


class PurchaseOrderLineWizard(models.TransientModel):
    _name = 'purchase.order.line.wizard'
    _description = 'Purchase Order Lines'

    name = fields.Text(string='Description', required=True)
    product_qty_sold = fields.Float(string='Quantity Sold', digits=dp.get_precision('Product Unit of Measure'), required=True)
    forecasted_qty = fields.Float(compute="_compute_forecasted_qty", string='Forecasted Quantity',
                                  digits=dp.get_precision('Product Unit of Measure'))
    product_qty_to_order = fields.Float(string='Quantity to Order', digits=dp.get_precision('Product Unit of Measure'))
    date_planned = fields.Datetime(compute="_compute_date_planned", string='Scheduled Date', index=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, required=True)
    partner_id = fields.Many2one('res.partner', related="supplier_id.name", string='Vendor')
    supplier_id = fields.Many2one('product.supplierinfo', string='Vendor/Supplier')
    order_id = fields.Many2one('purchase.order.wizard', string='Order Reference', index=True, required=True, ondelete='cascade')
    mto_product = fields.Boolean(string="MTO", help="Make To Order product")
    purchase_price = fields.Float('Unit Cost', digits=dp.get_precision('Product Price'),
                                  help="Cost used for stock valuation. Also used as a base price for pricelists. "
                                       "Expressed in the default unit of measure of the product.")
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    total_price = fields.Float(compute="_compute_total_price", string='Total Net Price', digits=dp.get_precision('Product Price'))
    seller_ids = fields.Many2many('product.supplierinfo', string='Possible Vendors')
    date_start = fields.Date('Start Date', related="supplier_id.date_start", help="Start date for this vendor price")
    date_end = fields.Date('End Date', related="supplier_id.date_end", help="End date for this vendor price")

    @api.depends('supplier_id', 'product_id', 'product_id.product_tmpl_id')
    def _compute_date_planned(self):
        for line in self:
            line.date_planned = datetime.now() + timedelta(days=max(
                0,
                line.supplier_id.delay,
                line.product_id.product_tmpl_id.sale_delay,
            ))

    @api.depends('product_qty_to_order', 'purchase_price', 'taxes_id', 'partner_id')
    def _compute_total_price(self):
        for line in self:
            line.update({
                'total_price': line.purchase_price * line.product_qty_to_order,
            })

    @api.onchange('product_qty_to_order')
    @api.depends('product_qty_to_order')
    def _compute_forecasted_qty(self):
        for line in self:
            line.update({
                'forecasted_qty': line.product_id.virtual_available - line.product_qty_sold,
            })

    @api.onchange('product_qty_to_order')
    def _onchange_qty_to_order(self):
        self.seller_ids = self.product_id.product_tmpl_id.seller_ids.filtered(
            lambda s: s.min_qty <= self.product_qty_to_order and self.order_id.check_date_availability(s))

    @api.onchange('supplier_id')
    def _onchange_purchase_price(self):
        for line in self:
            price = line.product_id.standard_price
            if line.supplier_id:
                price = line.supplier_id.price
            line.update({
                'purchase_price': price,
            })
