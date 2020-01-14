# Copyright 2020 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    scrap_percent = fields.Float(default=0)
