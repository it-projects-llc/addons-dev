# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ManageMembershipWizard(models.TransientModel):
    _name = 'sale_membership.manage_wizard'

    type_id = fields.Many2one('sale_membership.type', string='Type')
    reason = fields.Char(string='Reason')
    blocked = fields.Boolean(string='Blocked')

    @api.model
    def default_get(self, fields_list):
        defaults = super(ManageMembershipWizard, self).default_get(fields_list)
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for record in self.env['res.partner'].browse(active_ids):
            if 'type_id' in fields_list:
                defaults.setdefault('type_id', record.type_id.id)
                defaults.setdefault('blocked', record.blocked)
        return defaults


    @api.multi
    def save_changes(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for record in self.env['res.partner'].browse(active_ids):
            vals = {'partner_id': record.id,
                    'member_type_id': self.type_id.id,
                    'log_record_date': fields.Datetime.now(),
                    'reason': self.reason,
                    'name': self.type_id.name,
                    'blocked': self.blocked,
                    'points': record.points,
            }
            log_rec = self.env['sale_membership.log'].create(vals)
            record.points = self.type_id.points
            record.type_id = self.type_id.id
            record.blocked = self.blocked
