from odoo import models, fields


class Lot(models.Model):

    _inherit = 'stock.production.lot'

    length = fields.Float(digits=(16, 3))
    height = fields.Float(digits=(16, 3))
    width = fields.Float(digits=(16, 3))
