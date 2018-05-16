# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class Mrp_production(models.Model):
    _inherit = 'mrp.production'
    _rec_name = 'product_barcode'

    product_barcode = fields.Char(
        string="", required=True)
    receipt_barcode = fields.Char(
        string="")
    tag = fields.Char(
        string='tag #')
    partner_id = fields.Many2one(
        'res.partner',
        string="Customer name")
    street = fields.Char(
        string='Street')
    street2 = fields.Char(
        string='Street2')
    zip_no = fields.Char(
        string='Zip')
    city = fields.Char(
        string='City')
    state_id = fields.Many2one(
        'res.country.state',
        string="State")
    country_id = fields.Many2one(
        'res.country',
        string="Country")
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string="Price list")
    phone = fields.Char(
        string='Telphone1')
    phone2 = fields.Char(
        string='Telphone2')
    date = fields.Date(
        string='Date')
    finishing_date = fields.Date(
        string='Finishing Date')
    done_date = fields.Date(
        string='Done Date')
    delivery_date = fields.Date(
        string='Delivery Date')
    note = fields.Text(
        string='Note')
    warehouse_ids = fields.Many2many(
        'stock.warehouse')
    state = fields.Selection([
        ('planned', 'Started'),
        ('confirmed', 'Confirmed'),
        ('progress', 'Waiting Delivery'),
        ('cancel', 'Cancel'),
        ('done', 'Done')],
        string='Status',
        copy=False,
        default='planned',
        track_visibility='onchange')

    @api.multi
    def confirmed_order(self):
        type_view = self.env.context
        self.write({
            'state': 'confirmed',
        })
        if type_view['type_view'] == 'tree':
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.street = self.partner_id.street
        self.street2 = self.partner_id.street2
        self.city = self.partner_id.city
        self.zip_no = self.partner_id.zip
        self.state_id = self.partner_id.state_id
        self.country_id = self.partner_id.country_id
        self.pricelist_id = self.partner_id.property_product_pricelist

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
