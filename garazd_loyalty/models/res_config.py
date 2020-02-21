# -*- coding: utf-8 -*-

from odoo import api, fields, models


class BaseConfiguration(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)
    amount_for_card = fields.Float(
        related='company_id.amount_for_card',
        string='Purchase amount',
        help='Minimum One-time Purchase Amount for issuing a discount card.',
        readonly=False,
    )
    loyalty_approval = fields.Boolean('Manager approve Loyalty for Customer.')

    @api.model
    def get_default_amount_for_card(self, fields):
        amount_for_card = self.env.user.company_id.amount_for_card
        return {'amount_for_card': float(amount_for_card) or 0.0}

    @api.multi
    def set_amount_for_card(self):
        for record in self:
            self.env.user.company_id.amount_for_card = record.amount_for_card
