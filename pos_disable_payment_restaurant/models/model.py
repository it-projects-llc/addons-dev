# -*- coding: utf-8 -*-
# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'pos.config'

    group_decrease_kitchen_id = fields.Many2one(
        comodel_name='res.groups',
        compute='_compute_group_decrease_kitchen_id',
        string='Point of Sale - Allow Decrease Kitchen',
        help="This field is there to pass the id of the 'PoS - Allow Decrease Kitchen'"
        " Group to the Point of Sale Frontend.")

    group_remove_kitchen_order_line_id = fields.Many2one(
        comodel_name='res.groups',
        compute='_compute_group_remove_kitchen_order_line_id',
        string='Point of Sale - Allow Remove Kitchen Orderline',
        help="This field is there to pass the id of the 'PoS - Allow Remove Kitchen Orderline'"
        " Group to the Point of Sale Frontend.")

    @api.multi
    def _compute_group_decrease_kitchen_id(self):
        for config in self:
            self.group_decrease_kitchen_id = \
                self.env.ref('pos_disable_payment_restaurant.group_decrease_kitchen')

    @api.multi
    def _compute_group_remove_kitchen_order_line_id(self):
        for config in self:
            self.group_remove_kitchen_order_line_id = \
                self.env.ref('pos_disable_payment_restaurant.group_remove_kitchen_order_line')
