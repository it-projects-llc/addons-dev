# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectTaskSubtask(models.Model):
    _name = "project.task.subtask"
    _inherit = 'mail.thread'
    state = fields.Selection([('done', 'Done'),
                              ('todo', 'Todo'),
                              ('cancelled', 'Cancelled')],
                             'Status', required=True, copy=False, default='todo')
    done = fields.Boolean(track_visibility="onchange")
    name = fields.Char(required=True)
    reviewer_id = fields.Many2one('res.users', 'Reviewer', select=True, required=True)
    project_id = fields.Many2one("project.project", related='task_id.project_id', store=True)
    user_id = fields.Many2one('res.users', 'Assigned to', select=True, required=True)
    task_id = fields.Many2one('project.task', 'Task', ondelete='cascade', required=True, select="1")
    _track = {
        'done': {
            'subtask_project.mt_subtask_done': lambda self, cr, uid, obj, ctx=None: obj.done==True,
        }
    }

    @api.multi
    def write(self, vals):
        result = super(ProjectTaskSubtask, self).write(vals)
        for r in self:
            if vals.get('state'):
                template = self.env.ref('project_task_subtask.email_template_subtask_changed')
                email_ctx = {
                    'default_model': 'project.task.subtask',
                    'default_res_id': r.id,
                    'default_use_template': bool(template),
                    'default_template_id': template.id,
                }
                composer = self.env['mail.compose.message'].with_context(email_ctx).create({})
                composer.send_mail()
        return result

    # @api.model
    # def create(self, vals):
    #     try:
    #         result = super(ProjectTaskSubtask, self).create(vals)
    #     except:
    #         raise
    #     else:
    #         template = self.env.ref('project_task_subtask.email_template_subtask_create')
    #         email_ctx = {
    #             'default_model': 'project.task.subtask',
    #             'default_res_id': result.id,
    #             'default_use_template': bool(template),
    #             'default_template_id': template.id,
    #             }
    #         composer = self.env['mail.compose.message'].with_context(email_ctx).create({})
    #         composer.send_mail()
    #         return result


class Task(models.Model):
    _inherit = "project.task"
    subtask_ids = fields.One2many('project.task.subtask', 'task_id', 'Subtask')

    @api.multi
    def write(self, vals):
        result = super(Task, self).write(vals)
        for r in self:
            subtask_val = vals.get("subtask_ids")
            if subtask_val and subtask_val[0][0] == 0:
                print '\n\n\n\n', vals.get("subtask_ids"), '\n\n\n'
                template = self.env.ref('project_task_subtask.email_template_subtask_create')
                email_ctx = {
                    'default_model': 'project.task',
                    'default_res_id': r.id,
                    'default_use_template': bool(template),
                    'default_template_id': template.id,
                    'subtask': subtask_val[0][2]['name']
                }
                composer = self.env['mail.compose.message'].with_context(email_ctx).create({})
                composer.send_mail()
        return result
