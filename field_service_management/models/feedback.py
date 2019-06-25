# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import fields, models

AVAILABLE_PRIORITIES = [
    ('1', 'Unhappy'),
    ('2', 'Good'),
    ('3', 'Average'),
    ('4', 'Satisfied'),
    ('5', 'Happy'),
    ('6', 'Very Happy')
]


class JobFeedback(models.Model):
    _name = 'job.feedback'
    _description = 'Job Feedback'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner',
                                 string='Customer',
                                 help="Author of the rating",
                                 required=True)
    rating = fields.Selection(AVAILABLE_PRIORITIES, "Rating", default='1')
    feedback = fields.Text('Feedback', help="Reason of the rating")
    task_id = fields.Many2one('project.task',
                              string='Job',
                              help="Task on which the rating is given.")
    user_id = fields.Many2one(
        related='task_id.user_id', relation='res.users', string='Serviceman',
        store=True)
