# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchased_orders = fields.Integer(compute="_compute_purchased_orders_number",
                                      string="Quantity of Purchase Orders, based on that Sale Order")

    def _compute_purchased_orders_number(self):
        self.purchased_orders = len(self.env['purchase.order'].search([('sale_order_id', '=', self.id)]).ids)

    def create_purchase_order(self):
        view = self.env.ref('purchase_order_from_so.purchase_order_wizard_form')
        vals = {
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
            'sale_order_id': self.id,
        }
        wizard = self.env['purchase.order.wizard'].create(vals)
        wizard.create_po_lines_from_so(self)
        return {
            'name': _('Create wizard'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wizard.id,
            'context': vals,
        }


class SaleOrderLinePOfromSO(models.Model):
    _inherit = 'sale.order.line'

    no_forecasted_qty = fields.Boolean(compute="_compute_no_forecasted_qty", string='Positive Forecast',
                                       help="Forecasted quantity is not positive")

    @api.onchange('product_uom_qty')
    @api.depends('product_uom_qty')
    def _compute_no_forecasted_qty(self):
        for line in self:
            line.update({
                'no_forecasted_qty': line.product_id.type == 'product' and
                                     line.product_id.virtual_available - line.product_uom_qty < 0
            })

    @api.onchange('product_id')
    def _onchange_product_id_check_availability(self):
        # disables 'Not enough inventory' warning popup
        return {}


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order",
                                    help="Not empty if an origin for purchase order was sale order")
    customer_id = fields.Many2one('res.partner', string="Customer",
                                  help="Not empty if an origin for purchase order was sale order")
