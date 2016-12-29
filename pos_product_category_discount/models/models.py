# -*- coding: utf-8 -*-
from odoo import api, fields, models
import json


class PosCategoryDiscount(models.Model):

    _name = "pos.category_discount"

    category_discount_pc = fields.Float(string='Discount Percentage', default=10, help='The default discount percentage')
    discount_category_id = fields.Many2one("pos.category", string='Discount Category',
                                          help='The category used to model the discount')
    discount_program_id = fields.Many2one("pos.discount_program", string='Discount Program')


class PosDiscountProgram(models.Model):

    _name = "pos.discount_program"

    _description = "Discount Program"
    _rec_name = "discount_program_name"

    discount_program_name = fields.Char(string="Project name")
    discount_program_number = fields.Integer(string="Number")
    discount_category_ids = fields.One2many("pos.category_discount", "discount_program_id", string='Discount Category')

    # @api.multi
    # def get_category_discount(self):
    #
    #
    #     return json.dumps(self.discount_category_ids)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    discount_allowed = fields.Boolean(string='Discount allowed', help='Check if you want this product discount allowed in the Point of Sale', default=True)