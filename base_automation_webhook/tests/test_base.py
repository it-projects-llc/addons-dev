# Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestMessage(TransactionCase):
    at_install = True
    post_install = True

    def test_requests(self):
        """Check that requests package is available"""
        action = self.env['ir.actions.server'].create({
            'name': 'Action',
            'model_id': self.env.ref('base.model_res_partner'),
            'code': """requests.get"""
        })
        self.env['base.action.rule'].create({
            'name': 'Automation',
            'kind': 'on_create',
            'model_id': self.env.ref('base.model_res_partner'),
            'server_action_ids': [(4, action.id)]
        })
        self.env['res.partner'].create({'name': 'New Contact'})
