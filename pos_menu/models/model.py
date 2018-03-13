# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tag_ids = fields.Many2many('pos.tag', 'tag_ids_product_ids_rel', 'product_id', 'tag_id', string="Tags")


class PosConfig(models.Model):
    _inherit = 'pos.config'

    tag_ids = fields.Many2many('pos.tag', 'tag_ids_pos_ids_rel', 'pos_id', 'tag_id', string="Available Product Sets")


class PosTag(models.Model):
    _name = 'pos.tag'

    name = fields.Char(string='Name')
    product_ids = fields.Many2many('product.template', 'tag_ids_product_ids_rel', 'tag_id', 'product_id',
                                   domain="[('available_in_pos', '=', True)]", string="Products")
    pos_ids = fields.Many2many('pos.config', 'tag_ids_pos_ids_rel', 'tag_id', 'pos_id', string="POSes")
