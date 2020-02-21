from odoo import api, fields, models


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    applied_on = fields.Selection(selection_add=[
        ('4_product_vendor', 'Product Vendor')
    ])
    vendor_id = fields.Many2one('res.partner', 'Vendor')

    @api.onchange('applied_on')
    def _onchange_applied_on(self):
        super(PricelistItem, self)._onchange_applied_on()
        if self.applied_on != '4_product_vendor':
            self.vendor_id = False

    @api.onchange('vendor_id')
    def _onchange_vendor_id(self):
        if self.vendor_id == '4_product_vendor':
            self.price_surcharge = self.vendor_id.extra_price
