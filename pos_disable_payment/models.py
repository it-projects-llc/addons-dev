# Copyright 2015-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2016  manavi <https://github.com/manavi>
# Copyright 2017  invitu <https://github.com/invitu>
# Copyright 2017-2018  Ilmir Karamov <https://it-projects.info/team/ilmir-k>
# Copyright 2017-2018  David Arnold <https://github.com/blaggacao>
# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    allow_payments = fields.Boolean('Allow payments', default=True)
    allow_delete_order = fields.Boolean('Allow remove non-empty order', default=True)
    allow_discount = fields.Boolean('Allow discount', default=True)
    allow_edit_price = fields.Boolean('Allow edit price', default=True)
    allow_decrease_amount = fields.Boolean('Allow decrease quantity on order line', default=True)
    allow_delete_order_line = fields.Boolean('Allow remove order line', default=True)
    allow_create_order_line = fields.Boolean('Allow create order line', default=True)
    allow_refund = fields.Boolean('Allow refunds', default=True)
    allow_manual_customer_selecting = fields.Boolean('Allow manual customer selecting', default=True)

    @api.onchange('allow_decrease_amount')
    def _onchange_allow_decrease_amount(self):
        if self.allow_decrease_amount is False:
            self.allow_delete_order_line = False
