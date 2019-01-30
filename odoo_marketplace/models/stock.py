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

from odoo import models, fields, api, _
from lxml import etree
from datetime import datetime, timedelta
import odoo.addons.decimal_precision as dp
from odoo.tools.translate import _
from odoo.exceptions import except_orm, Warning, RedirectWarning
import logging
_logger = logging.getLogger(__name__)


class MarketplaceStock(models.Model):
    _name = "marketplace.stock"
    _inherit = ['mail.thread']
    _description = "Marketplace Stock"

    @api.model
    def _set_product_template(self):
        if self._context.get('active_model') == 'product.template':
            product_id = self.env['product.template'].browse(
                self._context.get('active_id'))
            return product_id.id
        else:
            product_id = self.env['product.product'].browse(
                self._context.get('active_id'))
            return product_id.product_tmpl_id.id if product_id else False
        seller_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_seller_group')[1]
        officer_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_officer_group')[1]
        groups_ids = self.env.user.sudo().groups_id.ids
        if seller_group in groups_ids and officer_group not in groups_ids:
            marketplace_seller_id = self.env.user.sudo().partner_id.id
            domain = {'product_temp_id':  [
                ('marketplace_seller_id', '=', marketplace_seller_id)]}
            return {'domain': domain}
        return self.env['product.template']

    @api.model
    def _set_product_id(self):
        if self._context.get('active_model') == 'product.template':
            product_ids = self.env['product.product'].search(
                [('product_tmpl_id', '=', self._context.get('active_id'))])
            return self.env['product.product'].browse(product_ids.ids[0]).id
        else:
            product_obj = self.env['product.product'].search([('id', '=', self._context.get('active_id'))])
            if product_obj:
                return product_obj.id


    @api.model
    def _get_product_location(self):
        if self._context.get('active_model') == 'product.template':
            product_ids = self.env['product.product'].search(
                [('product_tmpl_id', '=', self._context.get('active_id'))])
            product_obj = product_ids[0]
        else:
            product_obj = self.env['product.product'].search([('id', '=', self._context.get('active_id'))])
        if product_obj:
            if product_obj.location_id:
                return product_obj.location_id.id
            else:
                return product_obj.marketplace_seller_id.location_id.id

    @api.model
    def _set_title(self):
        msg = "Stock added on "
        current_date = datetime.today().strftime('%d-%B-%Y')
        title = msg + current_date
        return title

    name = fields.Char(string="Title", default=_set_title,
                       required=True,  translate=True)
    product_temp_id = fields.Many2one(
        'product.template', string='Product Template', default=_set_product_template)
    product_id = fields.Many2one(
        'product.product', string='Product', default=_set_product_id)
    marketplace_seller_id = fields.Many2one(
        "res.partner", related="product_id.marketplace_seller_id", string="Seller", store=True)
    new_quantity = fields.Float('New Quantity on Hand', default=1, digits=dp.get_precision(
        'Product Unit of Measure'), required=True, help='This quantity is expressed in the Default Unit of Measure of the product.', copy=False)
    location_id = fields.Many2one(
        'stock.location', 'Location', required=True, default=_get_product_location)
    state = fields.Selection([("draft", "Draft"), ("requested", "Requested"), (
        "approved", "Approved"), ("rejected", "Rejected")], string="Status", default="draft", copy=False)
    note = fields.Text("Notes",  translate=True)
    product_variant_count = fields.Integer('Variant Count', related='product_temp_id.product_variant_count')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(MarketplaceStock, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        seller_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_seller_group')[1]
        officer_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_officer_group')[1]
        groups_ids = self.env.user.sudo().groups_id.ids
        if seller_group in groups_ids and officer_group not in groups_ids:
            marketplace_seller_id = self.env.user.sudo().partner_id.id

            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='product_temp_id']"):
                node.set(
                    'domain', "[('type', '=', 'product'), ('status','=','approved'),('marketplace_seller_id', '=', %s)]" % marketplace_seller_id)
            for node in doc.xpath("//field[@name='product_id']"):
                node.set(
                    'domain', "[('type', '=', 'product'), ('status','=','approved'),('marketplace_seller_id', '=', %s)]" % marketplace_seller_id)
            res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        self.ensure_one()
        if self._context.get('active_model') == 'product.template':
            product_ids = self.env['product.product'].search([('product_tmpl_id', '=', self._context.get('active_id'))])
            result['domain'] = {'product_id': [
                        ('id', 'in', self.product_temp_id.product_variant_ids.ids), ('marketplace_seller_id', '!=', False), ('status', '=', 'approved')]}
            return result
        if self._context.get('active_model') == 'product.product':
            product_obj = self.env['product.product'].search([('id', '=', self._context.get('active_id'))])
            result['domain'] = {'product_id': [
                        ('id', 'in', [product_obj.id]), ('marketplace_seller_id', '!=', False), ('status', '=', 'approved')]}
            return result

        if self.product_id:
            self.product_temp_id = self.product_id.product_tmpl_id.id
            self.location_id = self.product_id.marketplace_seller_id.location_id.id or False,

    @api.multi
    def approve(self):
        for obj in self:
            if obj.state == "requested" and obj.product_id.status == "approved" and obj.product_id.marketplace_seller_id.state == "approved":
                obj.sudo().change_product_qty()
                obj.write({"state": "approved"})
            else:
                _logger.info("-------- MP inventory request can not be approved. Inventory request not in requested state or product is not approved or product seller is not approved. ----------")

    @api.multi
    def reject(self):
        for obj in self:
            if obj.state == "requested":
                obj.write({"state": "rejected"})


    @api.multi
    def set_2_draft(self):
        for obj in self:
            obj.write({"state": "draft"})

    @api.multi
    def request(self):
        for obj in self:
            if obj.new_quantity < 1:
                raise Warning(_("Quantity cannot be negative or 0."))
            obj.state = "requested"
            obj.auto_approve()

    @api.multi
    def auto_approve(self):
        for obj in self:
            if obj.marketplace_seller_id.auto_approve_qty:
                obj.approve()

    @api.multi
    def change_product_qty(self):
        inventory_obj = self.env['stock.inventory']
        inventory_line_obj = self.env['stock.inventory.line']
        for template_obj in self:
            if template_obj.new_quantity < 0:
                raise Warning(_('Initial Quantity can not be negative'))
            vals = {
                'product_id': template_obj.product_id.id,
                'product_tmpl_id': template_obj.product_temp_id.id,
                'new_quantity': template_obj.new_quantity,
                'location_id': template_obj.location_id.id,
            }
            wizard = self.env['stock.change.product.qty'].create(vals)
            wizard.change_product_qty()

    def disable_seller_all_inventory_requests(self, seller_id):
        if seller_id:
            inventory_obj = self.search(
                [("marketplace_seller_id", "=", seller_id), ('state', '!=', 'approved')])
            inventory_obj.reject()


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    marketplace_seller_id = fields.Many2one("res.partner", string="Seller")

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(StockPicking, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        officer_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_officer_group')[1]
        groups_ids = self.env.user.sudo().groups_id.ids
        if officer_group not in groups_ids and result.get("toolbar", False):
            toolbar_dict = result.get("toolbar", {})
            toolbar_dict["action"] = []
            toolbar_dict["relate"] = []
            for key in toolbar_dict:
                # Remove options from Print menu for seller
                if key == "print":
                    print_list = toolbar_dict[key]
                    for print_list_item in print_list:
                        if print_list_item["xml_id"] not in ["stock.action_report_delivery"]:
                            print_list.remove(print_list_item)
            result["toolbar"] = toolbar_dict
        return result

class StockMove(models.Model):
    _inherit = 'stock.move'

    marketplace_seller_id = fields.Many2one(
        "res.partner", related="product_id.marketplace_seller_id", string="Seller", store=True)

    @api.multi
    def _assign_picking(self):
        """Create a new picking for group of products belonging to seller(s)."""
        Picking = self.env['stock.picking']
        for move in self:
            domain = [
                ('group_id', '=', move.group_id.id),
                ('location_id', '=', move.location_id.id),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])]
            if move.product_id.marketplace_seller_id:
                domain.append(('marketplace_seller_id', '=',
                               move.product_id.marketplace_seller_id.id))
            else:
                domain.append(('marketplace_seller_id', '=', False))
            picking = Picking.search(domain, limit=1)
            if not picking:
                values = move._get_new_picking_values()
                values.update(
                    {"marketplace_seller_id": move.product_id.marketplace_seller_id.id})
                picking = Picking.create(values)
            move.write({'picking_id': picking.id})
        return True

    @api.multi
    def shipped_mp_move(self):
        for rec in self:
            rec.sudo().action_done()
            sol_obj = self.env["sale.order.line"].sudo().search(
                [('order_id.name', '=', rec.origin), ('product_id', '=', rec.product_id.id)], limit=1)
            if sol_obj:
                sol_obj.marketplace_state = "shipped"

    @api.multi
    def check_availability(self):
        for rec in self:
            rec.sudo().action_assign()

    @api.multi
    def write(self, values):
        result = super(StockMove, self).write(values)
        for rec in self:
            if rec.state == "cancel":
                sol_obj = self.env["sale.order.line"].sudo().search([('order_id.name', '=', rec.origin), ('product_id', '=', rec.product_id.id)], limit=1)
                if sol_obj:
                    sol_obj.marketplace_state = "cancel"
        return result
