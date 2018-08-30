# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hot_product = fields.Boolean(string='Hot Product', help='Check if you this product is hot product (promotion)',
                                 default=False)
    banner = fields.Binary(string='Hot product banner', attachment=True)
