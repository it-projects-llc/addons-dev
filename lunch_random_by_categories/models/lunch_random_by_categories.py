# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import random
from openerp.exceptions import UserError

class lunch_random_by_catergories(models.TransientModel):
    _inherit = 'lunch.order.line.lucky'
    
    category_ids = fields.Many2many(comodel_name='lunch.product.category', string='Category', domain=lambda self: [("id", "in", self.env['lunch.product'].search([]).mapped("category_id").ids)])
    
    @api.multi
    def random_pick(self):
        """
        To pick a random product from the selected categories, and create an order with this one
        """
        self.ensure_one()
        if self.is_max_budget:
            products_obj =  self.env['lunch.product'].search([('category_id', "in", self.category_ids.ids), ('price', '<=', self.max_budget)])
        else:
            products_obj =  self.env['lunch.product'].search([('category_id', "in", self.category_ids.ids)])
        if len(products_obj) != 0:
            random_product_obj = self.env['lunch.product'].browse([random.choice(products_obj.ids)])
            order_line = self.env['lunch.order.line'].create({
                'product_id': random_product_obj.id, 
                'order_id': self._context['active_id']
            })
        else:
            raise UserError(_('No product is matching your request. Now you will starve to death.'))