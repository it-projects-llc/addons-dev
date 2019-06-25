# See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    # state = fields.Selection([('draft', 'New'),
    #                           ('pending', 'Pending'),
    #                           ('open', 'In Progress'),
    #                           ('done', 'Done'),
    #                           ('cancelled', 'Cancelled')],
    #                          string='State',
    #                          help="Process of Job.")
    state = fields.Selection([('draft', 'New'),
                              ('reserved', 'Reserved'),
                              ('scheduled', 'Scheduled'),
                              ('open', 'In Progress'),
                              ('done', 'Complete'),
                              ('invoiced', 'Invoiced'),
                              ('cancelled', 'Cancelled'),
                              ('partial', 'Partially Complete')],
                             string='State',
                             help="Process of Job.")
    auto_assign = fields.Boolean('Auto-assign to new project?', default=False)
