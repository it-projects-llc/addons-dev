# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class ResUser(models.Model):
    _inherit = 'res.users'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        # if select a service immediate service person are visible and suggest
        context = self._context
        if context.has_key('assign_job'):
            if context.get('assign_job'):
                user_ids = self.env['emp.skill.line'].get_users_by_skill(
                    context.get('assign_job'))
                if user_ids:
                    args += [('id', 'in', user_ids)]
                else:
                    args += [('id', '=', False)]
            else:
                args += [('id', '=', False)]
        return super(ResUser, self)._search(
            args=args, offset=offset, limit=limit, order=order, count=count,
            access_rights_uid=access_rights_uid)

    @api.multi
    def set_serviceman(self):
        """
        Set Serviceman method throw set the user_id in jobs view
        """
        for user_rec in self:
            # set the serviceman record in browse and get the id set the
            # service person
            project_rec = self.env['project.task'].browse(
                self._context.get('job_id'))
            project_rec.write({'user_id': user_rec.id})
        return True
