# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)

# TODO: When inventory starts we set all stages to Done state.
#       If anybody is scanning yet he needs to get notification to finish.

class StockInventory(models.Model):
    _inherit = "stock.inventory"
    _order = 'date desc'

    stage_ids = fields.One2many(
        comodel_name='stock.inventory.stage',
        inverse_name='inventory_id',
        string='Stages',
    )
    stage_count = fields.Integer(
        string='Stages',
        compute='_compute_stages_count',
    )

    @api.depends('stage_ids')
    def _compute_stages_count(self):
        for inventory in self:
            inventory.stage_count = len(inventory.stage_ids)

    @api.model
    def _selection_filter(self):
        res_filter = super(StockInventory, self)._selection_filter()
        res_filter.append(('staged', _('Staged')))
        return res_filter

    @api.multi
    def action_start(self):
        for inventory in self:
            vals = {}
            if inventory.filter == 'staged':  # is_staged:
                vals.update({'line_ids': [(0, 0, line_values) for line_values in inventory._get_staged_inventory_lines_values()]})
            inventory.write(vals)
        result = super(StockInventory, self).action_start()
        return result
    prepare_inventory = action_start

    @api.multi
    def _get_staged_inventory_lines_values(self):
        for inventory in self:
            vals = []
            lines = {}
            stages = inventory.stage_ids

            # Lock all stages before starting inventory
            stages.write({'state': 'done'})

            for stage in stages:
                for line in stage.line_ids:
                    if line.product_id.id not in lines.keys():
                        qty = line.product_id.with_context(
                            compute_child=False,
                            location=inventory.location_id.id,
                        )._product_available()
                        theoretical_qty = qty[line.product_id.id]['qty_available']
                        product_data = {
                            'product_id': line.product_id.id,
                            'product_qty': line.qty,
                            'location_id': inventory.location_id.id,
                            'product_qty': line.qty,
                            'product_uom_id': line.product_id.uom_id.id,
                            'theoretical_qty': theoretical_qty,
                        }
                        lines[line.product_id.id] = product_data
                    else:
                        lines[line.product_id.id]['product_qty'] += line.qty
            if lines:
                vals = lines.values()
            else:
                raise Warning(_("Stages are empty."))
            return vals

    @api.multi
    def action_new_stage(self):
        for inventory in self:
            stage = self.env['stock.inventory.stage'].create({
                'name': inventory.name + ' - ' + self.env.user.name,
                'inventory_id': inventory.id,
                'user_id': self.env.user.id,
            })
            return {
                'type': 'ir.actions.act_window',
                'name': ('New Inventory Stage'),
                'res_model': 'stock.inventory.stage',
                'res_id': stage.id,
                'view_type': 'form',
                'view_mode': 'form',
                'flags': {'initial_mode': 'edit'},
            }
