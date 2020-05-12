# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    icon = fields.Binary(
        string='Icon',
        help='Icon of the service. This icon will be \
            shown in the android phone.')
    is_available_for_service = fields.Boolean(
        string='Available for Service',
        default=True,
        help='If checked the service is enabled and \
            will be shown in the android app')
    label_tasks = fields.Char(string='Use Tasks as',
                              default='Jobs',
                              help="Gives label 'Tasks' on\
                                  project's kanban view.")
    use_tasks = fields.Boolean(
        string='Use Jobs',
        help="Check this box to manage\
            internal activities through this project")
    service_hours = fields.Float()

    @api.model
    def create(self, vals):
        task_type_recs = self.env['project.task.type'].sudo().search(
            [('auto_assign', '=', True)])
        if task_type_recs:
            vals.update({'type_ids': [(6, 0, task_type_recs.ids)]})
        return super(ProjectProject, self).create(vals)

