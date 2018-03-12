# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tag_ids = fields.Many2many('pos.tag', 'tag_ids_product_ids_rel', 'product_id', 'tag_id', string="Tags")


class PosConfig(models.Model):
    _inherit = 'pos.config'

    tag_ids = fields.Many2many('pos.tag', 'tag_ids_pos_ids_rel', 'pos_id', 'tag_id', string="Tags")


class PosTag(models.Model):
    _name = 'pos.tag'

    name = fields.Char(string='Name')
    product_ids = fields.Many2many('product.template', 'tag_ids_product_ids_rel', 'tag_id', 'product_id',
                                   domain="[('available_in_pos', '=', True)]", string="Products")
    pos_ids = fields.Many2many('pos.config', 'tag_ids_pos_ids_rel', 'tag_id', 'pos_id', string="POSes")
