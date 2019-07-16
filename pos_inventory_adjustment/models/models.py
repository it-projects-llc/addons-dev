# -*- coding: utf-8 -*-
# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, _, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    inventory_adjustment = fields.Boolean('Inventory Mode')


class StockInventoryStage(models.Model):
    _inherit = "stock.inventory.stage"

    def update_stage_from_ui(self, data):
        stage_line_model = self.env['stock.inventory.stage.line']
        if self.state == 'done':
            return {
                'error': {
                    'title': 'Inventory Stage Status Error',
                    'message': 'Inventory Stage Was Already Done',
                }
            }
        self.line_ids.unlink()
        for line in data['lines']:
            product_id = line['product_id']
            qty = line['qty']
            same_produt_line = self.line_ids.filtered(lambda l: l.product_id.id == product_id)
            if same_produt_line:
                same_produt_line.write({
                    'qty': same_produt_line.qty + qty
                })
            else:
                stage_line_model.create({
                    'stage_id': self.id,
                    'product_id': product_id,
                    'qty': qty,
                })
        # self.action_stage_done()
        return {
            'inventory_stage_id': self.id,
        }
