# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.tools import html_escape as escape


SUBTASK_STATES = {'done': 'Done',
                  'todo': 'Todo',
                  'cancelled': 'Cancelled'}


class ProjectTaskSubtask(models.Model):
    _name = "project.task.subtask"
    state = fields.Selection([(k, v) for k, v in SUBTASK_STATES.items()],
                             'Status', required=True, copy=False, default='todo')
    name = fields.Char(required=True, string="Description")
    reviewer_id = fields.Many2one('res.users', 'Reviewer', compute="_compute_reviewer_id")
    project_id = fields.Many2one("project.project", related='task_id.project_id', store=True)
    user_id = fields.Many2one('res.users', 'Assigned to', select=True, required=True)
    task_id = fields.Many2one('project.task', 'Task', ondelete='cascade', required=True, select="1")

    @api.multi
    def _compute_reviewer_id(self):
        for record in self:
            record.reviewer_id = record.create_uid

    @api.multi
    def write(self, vals):
        result = super(ProjectTaskSubtask, self).write(vals)
        for r in self:
            if vals.get('state'):
                r.task_id.send_subtask_email(r.name, r.state)
        return result

    @api.multi
    def change_state_done(self):
        for record in self:
            record.state = 'done'

    @api.multi
    def change_state_todo(self):
        for record in self:
            record.state = 'todo'

    @api.multi
    def change_state_cancelled(self):
        for record in self:
            record.state = 'cancelled'


class Task(models.Model):
    _inherit = "project.task"
    subtask_ids = fields.One2many('project.task.subtask', 'task_id', 'Subtask')
    kanban_subtasks = fields.Text(compute='_compute_kanban_subtasks')

    @api.multi
    def _compute_kanban_subtasks(self):
        for record in self:
            result_string = '<ul>'
            for subtask in record.subtask_ids:
                if subtask.state == 'todo' and record.env.user == subtask.user_id:
                    tmp_string1 = 'From {0}: {1}'.format(subtask.reviewer_id.name, subtask.name)
                    result_string += '<li>{}</li>'.format(escape(tmp_string1))
            for subtask in record.subtask_ids:
                if subtask.state == 'todo' and record.env.user == subtask.reviewer_id:
                    tmp_string2 = 'To {0}: {1}'.format(subtask.user_id.name, subtask.name)
                    result_string += '<li>{}</li>'.format(escape(tmp_string2))
            record.kanban_subtasks = result_string + '</ul>'

    @api.multi
    def send_subtask_email(self, subtask_name, subtask_state):
        for r in self:
            template = self.env.ref('project_task_subtask.email_template_subtask_changed')
            email_ctx = {
                'default_model': 'project.task',
                'default_res_id': r.id,
                'default_use_template': bool(template),
                'default_template_id': template.id,
                'subtask_name': subtask_name,
                'subtask_state': SUBTASK_STATES[subtask_state],
            }
            composer = self.env['mail.compose.message'].with_context(email_ctx).create({})
            composer.send_mail()

    @api.multi
    def write(self, vals):
        result = super(Task, self).write(vals)
        for r in self:
            subtask_val = vals.get("subtask_ids")
            if subtask_val and subtask_val[0][0] == 0:
                r.send_subtask_email(subtask_val[0][2]['name'], subtask_val[0][2]['state'])
            return result
