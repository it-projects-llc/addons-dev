# Copyright 2020 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from datetime import datetime

from odoo import api, fields, models, _


class MrpWorkorder(models.Model):

    _inherit = 'mrp.workorder'

    @api.multi
    def button_preparing(self):
        self.ensure_one()

        self.button_pending()

        timeline = self.env['mrp.workcenter.productivity']

        for workorder in self:
            if workorder.production_id.state != 'progress':
                workorder.production_id.write({
                    'state': 'progress',
                    'date_start': datetime.now(),
                })
            timeline.create({
                'workorder_id': workorder.id,
                'workcenter_id': workorder.workcenter_id.id,
                'description': _('Time Tracking: ') + self.env.user.name,
                'date_start': datetime.now(),
                'user_id': self.env.user.id
            })
        return self.write({'state': 'progress', 'date_start': datetime.now()})
