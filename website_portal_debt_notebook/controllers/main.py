# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalDebtHistory(CustomerPortal):

    @http.route(['/my/debt_history', '/my/debt_history/<int:limit>'], type='http', auth="user", website=True)
    def portal_my_debt_history(self, limit=10):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        if partner:
            debts = partner.debt_history(limit=limit)[partner.id]
            values.update({
                'history': debts['history'],
                'debts': [value for key, value in debts['debts'].items()],
                'records_count': limit,
                'records_count_all': debts['records_count'],
                'page_name': 'debt',
            })

        return request.render("website_portal_debt_notebook.portal_my_debt_history", values)
