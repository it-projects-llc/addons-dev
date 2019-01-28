# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
import dateutil
from datetime import datetime

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	@api.multi
	def action_cancel(self):
		result = super(SaleOrder,self).action_cancel()
		for rec in self:
			if rec.state == 'cancel' and rec.order_line:
				mp_order_line = rec.order_line.filtered(lambda line: line.marketplace_seller_id != False)
				if mp_order_line:
					mp_order_line.write({'marketplace_state':'cancel'})
		return result

	@api.multi
	def action_draft(self):
		result = super(SaleOrder,self).action_draft()
		for rec in self:
			if rec.state == 'draft' and rec.order_line:
				mp_order_line = rec.order_line.filtered(lambda line: line.marketplace_seller_id != False)
				if mp_order_line:
					mp_order_line.write({'marketplace_state':'new'})
		return result


class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	@api.multi
	def name_get(self):
		result = []
		for record in self:
			result.append((record.id, record.order_id.name))
		return result

	marketplace_seller_id = fields.Many2one(
		related='product_id.marketplace_seller_id', string='Marketplace Seller', store=True, copy=False)
	marketplace_state = fields.Selection([("new","New"), ("approved","Approved") , ("shipped","Shipped"), ("cancel","Cancelled")], default="new", copy=False)
	mp_delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_seller_picking_ids')
	order_payment_acquirer_id = fields.Many2one("payment.acquirer", string="Payment Acquirer")
	order_payment_tx_id = fields.Many2one("payment.transaction", string="Transaction")

	order_carrier_id = fields.Many2one("delivery.carrier", related="order_id.carrier_id", string="Delivery Method")
	create_year = fields.Integer("Create Year",compute='_compute_create_year',store=True)

	@api.multi
	@api.depends('create_date')
	def _compute_create_year(self):
		for sol in self:
			sol.create_year = sol.create_date.year

	@api.multi
	@api.depends('order_id.procurement_group_id')
	def _compute_seller_picking_ids(self):
		for sol in self:
			sol.mp_delivery_count = len(sol.mapped('order_id.picking_ids').filtered(lambda picking: picking.marketplace_seller_id.id == sol.marketplace_seller_id.id))

	@api.multi
	def action_view_delivery(self):
		'''
		This function returns an action that display existing delivery orders
		of given sales order ids. It can either be a in a list or in a form
		view, if there is only one delivery order to show.
		'''
		action = self.env.ref('odoo_marketplace.marketplace_stock_picking_action').read()[0]

		pickings = self.mapped('order_id.picking_ids').filtered(lambda picking: picking.marketplace_seller_id.id == self.marketplace_seller_id.id)
		if len(pickings) > 1:
			action['domain'] = [('id', 'in', pickings.ids)]
		elif pickings:
			action['views'] = [(self.env.ref('odoo_marketplace.marketplace_picking_stock_modified_form_view').id, 'form')]
			action['res_id'] = pickings.id
		return action

	@api.multi
	def button_cancel(self):
		for rec in self:
			move_objs = self.env["stock.move"].search([('origin','=',rec.order_id.name), ('product_id','=', rec.product_id.id)])
			if move_objs:
				move_objs.action_cancel()
				rec.sudo().marketplace_state = "cancel"


	@api.multi
	def button_approve_ol(self):
		for rec in self:
			rec.sudo().marketplace_state = "approved"

	@api.multi
	def button_ship_ol(self):
		for rec in self:
			move_objs = self.env["stock.move"].sudo().search([('origin','=',rec.sudo().order_id.name), ('product_id','=', rec.product_id.id)],limit=1)
			for move_obj in move_objs:
				move_obj.action_done()
				if move_obj.state == "done":
					rec.sudo().marketplace_state = "shipped"
				else:
					raise Warning(_("Not able to done delivery order for this order. Please check the available quantity of the product. "))

	@api.multi
	def write(self, values):
		for rec in self:
			if 'qty_delivered' in values:
				if values["qty_delivered"] == rec.product_uom_qty:
					values.update({"marketplace_state" : "shipped"})
				if  values["qty_delivered"] > 0 and values["qty_delivered"] < rec.product_uom_qty:
					values.update({"marketplace_state" : "approved"})
		result = super(SaleOrderLine, self).write(values)
		return result
