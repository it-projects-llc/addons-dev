# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError, Warning, except_orm

class EmpSkillLines(models.Model):
    _name = 'emp.skill.line'
    _description = 'Employee Skill Lines'

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=True,
        help='Employee of the hr employee')
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Service',
        required=True,
        help='Skill of the Serviceman')
    rate_card = fields.Float(
        string='Service Rate (per hour)',
        help='Per hour work rate of employee for the specified service.')
    express_service_rate = fields.Float(
        string='Express Service Rate (per hour)',
        help='Additional charges that will be \
            added to the invoice if customer \
            wants the service in emergency.')

    @api.constrains('rate_card', 'express_service_rate')
    def _check_rates(self):
        if not self.rate_card or not self.express_service_rate:
            raise ValidationError(
                'Rate should be greater than zero.')
        if self.rate_card and self.rate_card > self.express_service_rate:
            raise ValidationError(
                'Express service rate should be greater than Service rate.')

    def get_users_by_skill(self, project_id):
        """
        get res users to Project skill for job view
        """
        user_ids = []
        project_line_recs = self.sudo().search(
            [('project_id', '=', project_id)])
        # get users to skill in hr.employee model for related user
        if project_line_recs:
            for project_line_rec in project_line_recs:
                if project_line_rec.employee_id.user_id:
                    user_ids.append(project_line_rec.employee_id.user_id.id)
        return user_ids or False

    def get_employee_by_skill(self, project_id):
        """
        get hr employee to Project skill for job view
        """
        employee_ids = []
        project_line_recs = self.sudo().search(
            [('project_id', '=', int(project_id))])
        # get employee record for service skill
        if project_line_recs:
            for project_line_rec in project_line_recs:
                if project_line_rec.employee_id:
                    employee_ids.append(project_line_rec.employee_id.id)
        return employee_ids or False

    def get_rate_for_skill(self, employee_id, project_id):
        """
        get Service rate for timesheet and invoice lines
        """
        project_line_rec = self.env['emp.skill.line'].search(
            [('employee_id', '=', employee_id),
             ('project_id', '=', project_id)])
        return project_line_rec and project_line_rec.rate_card or 0

    def get_express_rate_for_skill(self, employee_id, project_id):
        """
        get Express Service rate for timesheet and invoice lines
        """
        service_line_rec = self.env['emp.skill.line'].search(
            [('employee_id', '=', employee_id),
             ('project_id', '=', project_id)])
        return service_line_rec and service_line_rec.express_service_rate or\
            0
