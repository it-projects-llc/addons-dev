# -*- coding: utf-8 -*-

from openerp import models, fields


class ManageMembershipWizard(models.TransientModel):
    _name = 'sale_membership.manage_wizard'

    type_id = fields.Many2one('sale_membership.type', string='Type')
    reason = fields.Char(string='Reason')

    def default_get(self, cr, uid, fields, context=None):
        result = super(ManageMembershipWizard, self).default_get(cr, uid, fields, context=context)
        active_id = context and context.get('active_id', False)
        active_partner = self.pool['res.partner'].browse(cr, uid, active_id, context=context)
        if active_partner:
            result.update({
                'type_id': 1,
            })
        return result
