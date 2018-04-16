# -*- coding: utf-8 -*-
# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models


class ProductLabelSettings(models.TransientModel):
    _name = "product.label.report.settings"

    def _default_product_label(self):
        return self.product_id.default_label_id

    product_wizard_id = fields.Many2one('product.label.wizard')
    product_id = fields.Many2one('product.template', 'Product', required=True)
    quantity = fields.Integer("Quantity", default=1)
    label_id = fields.Many2one('product.label', 'Label', help="Select label for the product",
                               default=_default_product_label)


class ProductLabelWizard(models.TransientModel):
    _name = "product.label.wizard"
    _description = "Product Label wizard"

    def _default_product_ids(self):
        product_ids = self._context.get('active_model') == 'product.template' and self._context.get('active_ids') or []
        return [
            (0, 0, {'product_id': product.id, 'quantity': 1, 'label_id': product.default_label_id})
            for product in self.env['product.template'].browse(product_ids)
        ]

    settings_ids = fields.One2many('product.label.report.settings', 'product_wizard_id',
                                   string="Product Label",  default=_default_product_ids)

    @api.multi
    def print_labels_button(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'product_label_custom.report_product_label')
