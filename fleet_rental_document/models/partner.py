# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    rental_deposit_analytic_account_id = fields.Many2one('account.analytic.account', string='analytic deposit account for fleet rental customer', readonly=True)
    rental_payment_analytic_account_id = fields.Many2one('account.analytic.account', readonly=True)
