# Copyright 2020 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    scrap_percent = fields.Float(default=0)

    # Пока не продумал, как это поле использовать. Если будет время доработаю этот момент.
    # is_scrap_applied = fields.Boolean(default=False)
