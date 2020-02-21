from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    vendor_id = fields.Many2one('res.partner', "Vendor")

    @api.onchange('vendor_id', 'standard_price')
    def _compute_list_price(self):
        for rec in self:
            if rec.vendor_id:
                rec.list_price = rec.standard_price + rec.vendor_id.extra_price
