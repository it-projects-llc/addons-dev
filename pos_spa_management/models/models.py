# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    duration = fields.Integer('Duration', default=0)


class PosConfig(models.Model):
    _inherit = 'pos.order'

    user_id = fields.Many2one(states={})
    referrer_id = fields.Many2one(comodel_name='res.users', string='Referrer Person')

    @api.model
    def change_executor(self, user_id, order_ref):
        order = self.search([('pos_reference', '=', order_ref)])
        order.write({
            'user_id': user_id,
        })
        return order.id


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def get_name_by_phone(self, phone):
        partner = self.search([('phone', '=', phone)])
        if partner:
            return [partner.id, partner.name]
        return False
