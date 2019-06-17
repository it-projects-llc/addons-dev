# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    duration = fields.Integer('Duration', default=0)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    user_id = fields.Many2one(states={})
    referrer_id = fields.Many2one(comodel_name='res.partner', string='Referrer Person')
    executor_ids = fields.Many2many('res.users', string='Executors')

    @api.model
    def change_executor(self, user_id, order_ref, previous_user_id):
        order = self.search([('pos_reference', '=', order_ref)])
        vals = {
            'user_id': user_id,
            'executor_ids': [(4, user_id)],
        }
        order.lines.filtered(lambda ol: ol.user_id == previous_user_id).write(vals)
        order.write(vals)
        return order.id

    @api.model
    def _order_fields(self, ui_order):
        data = super(PosOrder, self)._order_fields(ui_order)
        data['referrer_id'] = ui_order.get('referrer_id', False)
        data['executor_ids'] = [(4, data['user_id'])]
        return data


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    user_id = fields.Many2one('res.users', string='Main Executor')
    executor_ids = fields.Many2many('res.users', string='Executors')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def get_name_by_phone(self, phone):
        partner = self.search([('phone', '=', phone)])
        if partner:
            return [partner.id, partner.name]
        return False
