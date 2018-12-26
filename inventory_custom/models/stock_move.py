from odoo import models, fields


class MoveLine(models.Model):

    _inherit = 'stock.move.line'

    product_tracking = fields.Selection(related='product_id.tracking')

    length = fields.Float(digits=(16, 3))
    height = fields.Float(digits=(16, 3))
    width = fields.Float(digits=(16, 3))

