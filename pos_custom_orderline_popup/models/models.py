# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api
import datetime
import copy


class ResPartner(models.Model):
    _inherit = "res.partner"

    birthday_date = fields.Date("Birthdate")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender", default='male')
    fathers_name = fields.Char('Fathers Name')
    surname = fields.Char('Surname')

    def update_partner_fields(self, partner_id, vals):
        partner_id = self.browse(int(partner_id))
        birthday_date = vals.get('birthday_date', False)
        # import wdb
        # wdb.set_trace()
        partner_id.write({
            'name': vals.get('name', False) or partner_id.name,
            'gender': vals.get('gender', False) or partner_id.gender,
            'surname': vals.get('surname', False) or partner_id.surname,
            'fathers_name': vals.get('fathers_name', False) or partner_id.fathers_name,
            'birthday_date': birthday_date and datetime.datetime.strptime(birthday_date, '%Y-%M-%d') or partner_id.birthday_date,
        })


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    seller_id = fields.Many2one('res.users', string="Seller")
    executor_id = fields.Many2one('res.users', string="Executor")
    partner_id = fields.Many2one('res.partner', string="Partner")
    service_room_id = fields.Many2one('service.room', string="Service Room")
    guest_category_id = fields.Many2one('guest.category', string="Guest Category")


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _process_order(self, pos_order):
        pos_order = copy.deepcopy(pos_order)
        for l in pos_order['lines']:
            l = l[2]
            partner_id = l.get('partner_id', False)
            if partner_id:
                l['partner_id'] = int(partner_id)
                # l['seller_id'] = int(l.get('seller_id', 0))
                # l['executor_id'] = int(l.get('executor_id', 0))
                self.env['res.partner'].update_partner_fields(partner_id, l.get('partner_vals', {}))

        order = super(PosOrder, self)._process_order(pos_order)
        return order


class GuestCategory(models.Model):
    _name = "guest.category"

    name = fields.Char('Name')


class ServiceRoom(models.Model):
    _name = "service.room"

    name = fields.Char('Name')
