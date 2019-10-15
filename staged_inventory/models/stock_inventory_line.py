# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    stage_ids = fields.Many2many(
        comodel_name='stock.inventory.stage',
        string='Stages',
        compute='_get_product_inventory_stages',
        readonly=True,
    )

    @api.multi
    def _get_product_inventory_stages(self):
        """ Get inventory stages of product."""
        for line in self:
            stages = self.env['stock.inventory.stage.line'].search([
                ('stage_id.inventory_id', '=', line.inventory_id.id),
                ('product_id', '=', line.product_id.id),
            ])
            _logger.debug("\n   >>>   _get_product_inventory_stages: stages={}".format(stages))
            ids = set(stages.mapped('stage_id').ids)
            line.stage_ids = [(6, 0, ids)]
