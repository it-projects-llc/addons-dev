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
        string='Stages of Inventory',
    )
    stage_count = fields.Integer(
        string='Stages',
        compute='_compute_stages_count',
    )
    total_real_amount = fields.Float(
        string='Total Real Amount',
        compute="_compute_total_real_amount",
    )
    total_theoretical_amount = fields.Float(
        string='Total Theoretical Amount',
        compute="_compute_total_theoretical_amount",
    )
    exhausted_product_ids = fields.Many2many(
        comodel_name='product.product',
        string='Exhausted Products',
        # readonly=True,
        # store=False,
        # compute='_get_exhausted_product_in_location',
    )

    @api.depends('stage_ids')
    def _compute_stages_count(self):
        for inventory in self:
            inventory.stage_count = len(inventory.stage_ids)

    @api.depends('stage_ids', 'line_ids')
    def _compute_total_real_amount(self):
        for inv in self:
            inv.total_real_amount = sum([l.real_amount for l in inv.line_ids] + [0])

    @api.depends('stage_ids', 'line_ids')
    def _compute_total_theoretical_amount(self):
        for inv in self:
            inv.total_theoretical_amount = sum([l.theoretical_amount for l in inv.line_ids] + [0])

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
                vals.update({'line_ids': [
                    (0, 0, line_values) for line_values in inventory._get_staged_inventory_lines_values()
                ]})
            inventory.write(vals)

        # Get list of unscanned products
        products = self.env['product.product'].search([])
        quantities = products.with_context(location=inventory.location_id.id)._product_available()
        unscanned_products = []
        products_in_inventory = inventory.line_ids.mapped('product_id')
        print("products_in_inventory = %s" % products_in_inventory)
        for product in products:
            if quantities[product.id]['qty_available'] != 0:
                # products_in_location.append(product.id)
                # print("product = %s" % product)
                if product.id not in products_in_inventory.ids:
                    unscanned_products.append(product.id)
                    inventory.exhausted_product_ids = [(4, product.id)]
        print("unscanned_products = %s" % unscanned_products)

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

    # @api.multi
    # def update_from_stages(self):
    #     for inventory in self:
    #         vals = {}
    #         if inventory.filter == 'staged':
    #             inventory.line_ids.unlink()
    #             vals.update({'line_ids': [
    #                 (0, 0, line_values) for line_values in inventory._get_staged_inventory_lines_values()
    #             ]})
    #             inventory.write(vals)

        # # Get list of unscanned products
        # products = self.env['product.product'].search([])
        # # print("products = %d" % len(products))
        # quantities = products.with_context(location=self.location.id)._product_available()
        # # print("quantities = %d" % len(quantities))
        # unscanned_products = []
        # products_in_inventory = self.inventory.line_ids.mapped('product_id')
        # print("products_in_inventory = %s" % products_in_inventory)
        # for product in products:
        #     if quantities[product.id]['qty_available'] != 0:
        #         # products_in_location.append(product.id)
        #         # print("product = %s" % product)
        #         if product.id not in products_in_inventory.ids:
        #             unscanned_products.append(product.id)
        # print("unscanned_products = %s" % unscanned_products)

    @api.multi
    def action_validate(self):
        # Add lines with exhausted products
        for inventory in self:
            if inventory.filter == 'staged':
                for product in inventory.exhausted_product_ids:
                    qty = product.with_context(
                        compute_child=False,
                        location=inventory.location_id.id,
                    )._product_available()
                    theoretical_qty = qty[product.id]['qty_available']
                    line_vals = {
                        'product_id': product.id,
                        'product_qty': 0.0,
                        'location_id': inventory.location_id.id,
                        'product_uom_id': product.uom_id.id,
                        'theoretical_qty': theoretical_qty,
                        'inventory_id': inventory.id,
                    }
                    # _logger.debug("\n   >>>   action_validate: line_vals={}".format(line_vals))
                    self.env['stock.inventory.line'].create(line_vals)
        res = super(StockInventory, self).action_validate()
        return res


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    product_barcode = fields.Char(related="product_id.barcode", string='Barcode')
    real_amount = fields.Float(compute="_compute_real_amount", string='Real Amount')
    theoretical_amount = fields.Float(compute="_compute_theoretical_amount", string='Theoretical Amount')

    @api.onchange('product_qty', 'product_id', 'product_id.lst_price')
    @api.depends('product_qty', 'product_id', 'product_id.lst_price')
    def _compute_real_amount(self):
        # import wdb
        # wdb.set_trace()
        for line in self:
            line.real_amount = line.product_qty * line.product_id.lst_price

    @api.onchange('theoretical_qty', 'product_id', 'product_id.lst_price')
    @api.depends('theoretical_qty', 'product_id', 'product_id.lst_price')
    def _compute_theoretical_amount(self):
        for line in self:
            line.theoretical_amount = line.theoretical_qty * line.product_id.lst_price
