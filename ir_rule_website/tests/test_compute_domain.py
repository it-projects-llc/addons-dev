# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestComputeDomain(TransactionCase):
    at_install = True
    post_install = True

    def test_base(self):
        IrRule = self.env['ir.rule']
        rule = IrRule.create({'name': 'test ir_rule_website',
                              'model_id': self.env.ref('base.model_res_partner').id,
                              'domain_force': "[('parent_id', 'in', [website_id])]"})
        demo_user = self.env.ref('base.group_system')
        website_id = 1
        test_domain = ('parent_id', 'in', [website_id])
        domain = IrRule.sudo(user=demo_user.id).with_context(website_id=website_id)._compute_domain('res.partner')
        self.assertTrue(test_domain in domain)
