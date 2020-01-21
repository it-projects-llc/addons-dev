# Copyright 2020 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # custom_field_id = fields.Many2one('mrp.eurodesign')

    def button_apply_package_piking(self):
        self.ensure_one()
        for unit in self.move_ids_without_package:
            unit.product_uom_qty = unit.product_id.product_qty
        print('Picking applied')


class EuroDesign(models.Model):

    # пока делаю как отдельную модель, чтобы не было путницы, когда появятся соображения о том как лучше можно лучше,
    # внедрить эту модель, то переделаю
    # _inherit = 'stock.picking'
    _name = 'mrp.eurodesign'
    _description = 'Custom model, needs to change'

    product_id = fields.Many2one('product.product')
    package_qty = fields.Float()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_qty = fields.Float()

    # package_custom_ids = fields.One2many('mrp.eurodesign', 'product_id')


