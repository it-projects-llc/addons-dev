# Copyright 2020 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MrpWorkcenterProductivityLossType(models.Model):
    _inherit = "mrp.workcenter.productivity.loss.type"

    loss_type = fields.Selection(selection_add=[('preparing', 'Preparing')])


class MrpWorkorder(models.Model):

    _inherit = 'mrp.workorder'

    @api.multi
    def button_preparing(self):
        self.button_pending()
        timeline = self.env['mrp.workcenter.productivity']
        loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type', '=', 'preparing')], limit=1)

        if not len(loss_id):
            raise UserError(_(
                "You need to define at least one productivity loss in the category 'Productivity'. "
                "Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))

        for workorder in self:
            if workorder.production_id.state != 'progress':
                workorder.production_id.write({
                    'state': 'progress',
                    'date_start': datetime.now(),
                })
            timeline.create({
                'workorder_id': workorder.id,
                'workcenter_id': workorder.workcenter_id.id,
                'description': _('Time Tracking: ')+self.env.user.name,
                'loss_id': loss_id[0].id,
                'date_start': datetime.now(),
                'user_id': self.env.user.id
            })
        return self.write({'state': 'progress',
                    'date_start': datetime.now(),
        })
