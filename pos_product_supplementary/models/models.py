# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    supplementary_products = fields.Boolean('Sell Supplementary Products')
    hide_supplementary_products = fields.Boolean('Hide Supplementary Products',
                                                 help='All supplementary products will be displayed in POS'
                                                      'even if the option `Available in POS` is disabled')


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    parented_orderline = fields.Many2one('pos.order.line', string='Sell Supplementary Products')
    supplementary_line_ids = fields.One2many('pos.order.line', 'parented_orderline', string='Base Product')

    @api.model
    def create(self, values):
        if values.get('parented_orderline'):
            del values['parented_orderline']
        if values.get('supplementary_line_ids'):
            del values['supplementary_line_ids']
        return super(PosOrderLine, self).create(values)
