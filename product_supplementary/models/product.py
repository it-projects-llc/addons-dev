# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.template'

    is_supplementary_product = fields.Boolean('Supplementary Product')
    supplementary_product_child_ids = fields.Many2many('product.product', 'product_template_supplementary_product',
                                                       'supplementary_product_child_ids',
                                                       'supplementary_product_parent_ids',
                                                       string='Supplementary Products',
                                                       help='List of Supplementary Products')
    supplementary_product_parent_ids = fields.Many2many('product.template', 'product_template_supplementary_product',
                                                        'supplementary_product_parent_ids',
                                                        'supplementary_product_child_ids',
                                                        string='Parented Products',
                                                        help='List of Parented Products')

    @api.onchange('is_supplementary_product')
    def _onchange_is_supplementary_product(self):
        self.supplementary_product_parent_ids = False
        self.supplementary_product_child_ids = False


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_supplementary_product = fields.Boolean('Supplementary Product')
    supplementary_product_child_ids = fields.Many2many('product.product', 'product_product_supplementary_product',
                                                       'supplementary_product_child_ids',
                                                       'supplementary_product_parent_ids',
                                                       string='Supplementary Products',
                                                       help='List of Supplementary Products')
    supplementary_product_parent_ids = fields.Many2many('product.product', 'product_product_supplementary_product',
                                                        'supplementary_product_parent_ids',
                                                        'supplementary_product_child_ids',
                                                        string='Parented Products',
                                                        help='List of Parented Products')

    @api.onchange('is_supplementary_product')
    def _onchange_is_supplementary_product(self):
        self.supplementary_product_parent_ids = False
        self.supplementary_product_child_ids = False
