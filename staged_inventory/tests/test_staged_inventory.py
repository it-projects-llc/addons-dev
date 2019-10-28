# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestStagedInventory(TransactionCase):

    def create_product(self, name):
        return self.env['product.product'].create({
            'name': name,
            'type': 'product',
            'uom_id': self.env.ref('product.product_uom_unit').id,
            'uom_po_id': self.env.ref('product.product_uom_unit').id,
        })

    def change_product_qty(self, product, qty, location):
        wizard = self.env['stock.change.product.qty'].create({
            'product_id': product.id,
            'new_quantity': qty,
            'location_id': location.id,
        })
        wizard.change_product_qty()

    def create_stage(self, name, inventory):
        stage = self.env['stock.inventory.stage'].create({
            'name': name,
            'inventory_id': inventory.id,
        })
        return stage

    def add_product_to_stage(self, stage, product, qty=1.0):
        stage_line = self.env['stock.inventory.stage.line'].create({
            'stage_id': stage.id,
            'product_id': product.id,
            'qty': qty,
        })
        return stage_line

    def setUp(self):
        super(TestStagedInventory, self).setUp()
        # self.location = self.env.ref('stock.stock_location_stock')
        self.location = self.env['stock.location'].create({
            'name': 'Test location',
            'usage': 'internal',
        })
        self.inventory = self.env['stock.inventory'].create({
            'name': 'Test Inventory',
            'location_id': self.location.id,
            'filter': 'staged',
        })
        self.product_1 = self.create_product('Product 1')
        # self.env.ref('product.product_product_4')
        # _logger.debug("   >>>   Test SetUp: Product 1={}".format(self.product_1))
        self.change_product_qty(self.product_1, 5, self.location)

        self.product_2 = self.create_product('Product 2')
        self.change_product_qty(self.product_2, 2, self.location)

        self.product_3 = self.create_product('Product 3')
        self.change_product_qty(self.product_3, 3, self.location)

        # Product with negative quantity
        self.product_4 = self.create_product('Product 4')
        picking = self.env['stock.picking'].create({
            'location_id': self.location.id,
            'location_dest_id': self.env.ref('stock.stock_location_scrapped').id,
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
            'move_lines': [(0, 0, {
                'name': self.product_4.name,
                'product_id': self.product_4.id,
                'product_uom': self.product_4.uom_id.id,
                'product_uom_qty': 1.0,
            })],
        })
        picking.action_confirm()
        picking.force_assign()
        # picking.action_assign()
        picking.pack_operation_product_ids.write({'qty_done': 1.0})
        # pack_opt = self.env['stock.pack.operation'].search([('picking_id', '=', picking.id)], limit=1)
        # print("pack_opt = %s" % pack_opt)
        # pack_opt.qty_done = 1.0
        picking.do_new_transfer()

    def test_000_check_quantities_before_inventory(self):
        product_1_qty = self.product_1.with_context(
            compute_child=False,
            location=self.location.id,
        )._product_available()
        # print(product_1_qty[self.product_1.id]['qty_available'])
        self.assertEqual(product_1_qty[self.product_1.id]['qty_available'], 5)

        product_4_qty = self.product_4.with_context(
            compute_child=False,
            location=self.location.id,
        )._product_available()
        self.assertEqual(product_4_qty[self.product_4.id]['qty_available'], -1)

    def test_001_staged_inventory_done(self):
        self.stage_1 = self.create_stage('Stage 1', self.inventory)
        self.stage_1.line_ids = [(0, 0, {
            'stage_id': self.stage_1.id,
            'product_id': self.product_1.id,
            'qty': 4,
        })]
        self.stage_2 = self.create_stage('Stage 2', self.inventory)
        self.stage_2.line_ids = [(0, 0, {
            'stage_id': self.stage_2.id,
            'product_id': self.product_2.id,
            'qty': 3,
        })]

        self.inventory.prepare_inventory()

        # Get list of unscanned products
        products = self.env['product.product'].search([])
        # print("products = %d" % len(products))
        quantities = products.with_context(location=self.location.id)._product_available()
        # print("quantities = %d" % len(quantities))
        unscanned_products = []
        products_in_inventory = self.inventory.line_ids.mapped('product_id')
        print("products_in_inventory = %s" % products_in_inventory)
        for product in products:
            if quantities[product.id]['qty_available'] != 0:
                # products_in_location.append(product.id)
                # print("product = %s" % product)
                if product.id not in products_in_inventory.ids:
                    unscanned_products.append(product.id)
        print("unscanned_products = %s" % unscanned_products)

        # Add unscanned products with quantity equal 0
        for product_id in unscanned_products:
            self.env['stock.inventory.line'].create({
                'product_id': product_id,
                'inventory_id': self.inventory.id,
                'product_uom_id': self.env['product.product'].browse(product_id).uom_id.id,
                # 'product_qty': 0.0,
                'location_id': self.location.id,
            })

        self.inventory.action_done()

        product_1_move = self.inventory.move_ids.filtered(lambda x: x.product_id == self.product_1)
        self.assertEqual(len(product_1_move), 1, 'Move line not exist.')
        self.assertEqual(product_1_move.product_uom_qty, 1)
        self.assertEqual(product_1_move.location_dest_id, self.env.ref('stock.location_inventory'))

        product_2_move = self.inventory.move_ids.filtered(lambda x: x.product_id == self.product_2)
        self.assertEqual(product_2_move.product_uom_qty, 1)
        self.assertEqual(product_2_move.location_dest_id, self.location)

        product_3_move = self.inventory.move_ids.filtered(lambda x: x.product_id == self.product_3)
        self.assertEqual(product_3_move.product_uom_qty, 3)
        self.assertEqual(product_3_move.location_dest_id, self.env.ref('stock.location_inventory'))
        # print(self.stage_1.line_ids[0].qty)
        # print(self.stage_2.line_ids[0].qty)

        # Check available products after inventory
        product_1_final_qty = self.product_1.with_context(location=self.location.id)._product_available()
        self.assertEqual(product_1_final_qty[self.product_1.id]['qty_available'], 4)
        product_2_final_qty = self.product_2.with_context(location=self.location.id)._product_available()
        self.assertEqual(product_2_final_qty[self.product_2.id]['qty_available'], 3)
        product_3_final_qty = self.product_3.with_context(location=self.location.id)._product_available()
        self.assertEqual(product_3_final_qty[self.product_3.id]['qty_available'], 0)
        product_4_final_qty = self.product_4.with_context(location=self.location.id)._product_available()
        self.assertEqual(product_4_final_qty[self.product_4.id]['qty_available'], 0)
