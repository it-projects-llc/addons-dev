# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    show_orderline_default_pricelist = fields.Boolean(string="Default Pricelist for Orderline", default=False)


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    pos_discount_policy = fields.Selection([('with_discount', 'Discount included in the price in POS'),
                                            ('without_discount', 'Show public price & discount to the customer in POS')],
                                           default='with_discount', string="POS Discount")
