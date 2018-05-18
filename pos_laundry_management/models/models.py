# -*- coding: utf-8 -*-
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api
from odoo import fields
from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    phonetic_name = fields.Char('Phonetic Name')

    @api.multi
    def load_history(self, limit=0):
        """
        :param int limit: max number of records to return
        :return: dictionary with keys:
             * partner_id: partner identification
             * history: list of dictionaries
                 * date
                 * receipt_barcode
                 * state
                 * finishing_date
                 * product_id
                 * product_barcode
                 * product tag
                 * warehouse_ids
                    * complete_name
                 * state
                 * partner_id
        """
        fields = [
            'date',
            'receipt_barcode',
            'state',
            'finishing_date',
            'product_id',
            'product_barcode',
            'tag',
            'warehouse_ids',
            'state',
            'partner_id',
        ]
        data = dict((id, {'history': [],
                          'partner_id': id,
                          }) for id in self.ids)
        for partner_id in self.ids:
            records = self.env['mrp.production'].search_read(
                domain=[('partner_id', '=', partner_id)],
                fields=fields,
                limit=limit,
            )
            data[partner_id]['history'] = records
            for line in data[partner_id]['history']:
                whs = []
                for wh in line['warehouse_ids']:
                    whs.append(self.env["stock.warehouse"].browse(wh).lot_stock_id)
                line['warehouse_ids'] = map(lambda w: w.complete_name, whs)
        return data


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    # redefined field with the new attribute required=True
    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material', required=True,
        readonly=True, states={'confirmed': [('readonly', False)]},
        help="Bill of Materials allow you to define the list of required raw materials to make a finished product.")

    @api.one
    def set_state(self, new_state):
        self.write({
            'state': new_state,
        })
        return self.env['res.partner'].browse(self.partner_id.id).load_history(None)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create_from_ui(self, orders):
        order_ids = super(PosOrder, self).create_from_ui(orders)
        for order in self.browse(order_ids):
            for line in order.lines:
                product = line.product_id
                if product.bom_ids and line.pack_lot_ids:
                    for lot in line.pack_lot_ids:
                        partner_id = order.partner_id and order.partner_id.id or False
                        production = self.env['mrp.production'].create({
                            'product_id': product.id,
                            'product_qty': line.qty,
                            'bom_id': product.bom_ids[0].id,
                            'product_uom_id': product.uom_id.id,
                            'product_barcode': lot.lot_name,
                            'tag': lot.tag,
                            'origin': order.name,
                            'receipt_barcode': order.pos_reference,
                            'partner_id': partner_id,
                            'date': fields.Datetime.now(),
                        })
                        if partner_id:
                            production._onchange_partner_id()
        return order_ids


class PosOrderLineLot(models.Model):
    _inherit = "pos.pack.operation.lot"

    tag = fields.Integer('Tag')
