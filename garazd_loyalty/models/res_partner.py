# -*- coding: utf-8 -*-
# Copyright (C) 2018 Razumovskyi Yurii <GarazdCreation@gmail.com>

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError


class GarazdPartner(models.Model):
    _inherit = "res.partner"

    loyalty_date = fields.Datetime(
        'Card Issued',
        help='The Date of issue Loyalty card.',
    )
    loyalty_type = fields.Selection(
        [
            ('none', 'Discount not provided'),
            ('fixed', 'Fixed customer discount'),
            ('purchase', 'Customer discount based on purchases amount')
        ],
        string='Loyalty Type',
        default='none',
        help='Loyalty type for customer.',
    )
    loyalty_id = fields.Many2one('garazd.loyalty', string='Level')
    loyalty_discount = fields.Integer(string='Discount, %')
    amount_before_loyalty = fields.Float(
        string='Amount of purchases',
        help='Amount of purchases before using the loyalty system.',
    )

    @api.model
    def create(self, values):
        record = super(GarazdPartner, self).create(values)
        if record.barcode:
            record.loyalty_date = fields.Datetime.now()
        return record

    @api.multi
    def write(self, vals):
        result = False
        for partner in self:
            prev_barcode = partner.barcode
            result = super(GarazdPartner, partner).write(vals)
            if not prev_barcode and partner.barcode:
                partner.loyalty_date = fields.Datetime.now()
        return result

    @api.onchange('amount_before_loyalty')
    def _onchange_amount_before_loyalty(self):
        self.ensure_one()
        if self.loyalty_type == 'purchase':
            self.set_loyalty_level()

    @api.depends('loyalty_id')
    def _apply_discount(self):
        self.filtered(lambda x: x.loyalty_type == 'purchase').set_loyalty_level()

    @api.onchange('loyalty_type')
    def _onchange_loyalty_id(self):
        self.ensure_one()
        if self.loyalty_type == 'none':
            self.write({
                'loyalty_id': None,
                'loyalty_discount': 0.0,
            })
        elif self.loyalty_type == 'fixed':
            self.write({
                'loyalty_id': None,
            })
        elif self.loyalty_type == 'purchase':
            self.set_loyalty_level()

    @api.multi
    def get_purchase_amount(self):
        total_amount = 0.0
        for partner in self:
            pos_sales = sum(pos_sale.amount_total
                for pos_sale in self.env['pos.order'].search(
                    [('partner_id', '=', partner.id), ('state', 'in', ['paid', 'done'])]))
            orders = partner.env['pos.order'].search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['paid', 'done'])
            ])
            total_amount += pos_sales + partner.amount_before_loyalty
        return total_amount

    @api.multi
    def set_loyalty_level(self):
        for partner in self.filtered(lambda x: x.customer and x.loyalty_type == 'purchase'):
            purchase_amount = partner.get_purchase_amount()
            loyalty_levels = self.env['garazd.loyalty'].search([], order="amount_from desc")
            for level in loyalty_levels:
                if purchase_amount >= level.amount_from:
                    partner.write({
                        'loyalty_id': level.id,
                        'loyalty_discount': level.percent,
                    })
                    partner.update({
                        'loyalty_id': level.id,
                        'loyalty_discount': level.percent,
                    })
                    break
