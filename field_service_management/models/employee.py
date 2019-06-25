# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError, Warning, except_orm


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    emp_skill_ids = fields.One2many(
        comodel_name='emp.skill.line',
        inverse_name='employee_id',
        string='Employee Skills',
        help='The services provided by the serviceman.')
    zone_ids = fields.Many2many(
        comodel_name='zone.zone',
        relation='zone_rel',
        column1='tm_id',
        column2='zone_id',
        string="Zone",
        help='Zones that belong to the person.')
    state_ids = fields.Many2many(
        comodel_name='res.country.state',
        relation='state_rel',
        column1='tm_id',
        column2='state_id',
        string="States",
        help='States that belong to the person.')
    city_ids = fields.Many2many(
        comodel_name='city.city',
        relation='city_rel',
        column1='tm_id',
        column2='city_id',
        string="City",
        help='City that belong to the person.')
    area_ids = fields.Many2many(
        comodel_name='area.area',
        relation='area_rel',
        column1='tm_id',
        column2='area_id',
        string="Area",
        help='Areas that belong to the person')
    is_serviceman = fields.Boolean(
        string='Serviceman',
        help='if checked the partner is a serviceman')
    is_operator = fields.Boolean(
        string='Operator',
        help='if checked the partner is an operator.')
    is_manager = fields.Boolean(
        string='Manager',
        help='if checked the partner is a manager.')
    feedback_efficiency = fields.Float(compute='_feedback_count',
                                       digits=(16,2))
    
    @api.multi 
    def _feedback_count(self):
        feedback_obj = self.env['job.feedback']
        for rec in self:
            job_ids = feedback_obj.search([('user_id','=',rec.user_id.id),
                                            ('task_id.stage_id.state','=','done')])
            totl_ratings = 0
            totl_ratings = sum([int(job_rec.rating) for job_rec in job_ids if job_ids])
            if len(job_ids) != 0:
                rec.feedback_efficiency = totl_ratings / len(job_ids)

    @api.multi
    def create_user(self, password=False):
        """Create user from Employee."""
        # Raise warning if the email is not entered in the new record.
        if not self.work_email:
            raise ValidationError('Please Enter Email!')
        # Creating the vals dictionary for a new user.
        user_vals = {
            'name': self.name,
            'login': self.work_email,
            'phone': self.work_phone,
            'customer': False,
            'password': password or self.company_id.default_password
        }
        if self.is_serviceman:
            user_vals.update({
                'is_serviceman': True,
                'groups_id': [(6, 0, [self.env.ref('field_service_management.group_serviceman').id])],
            })
        elif self.is_operator:
            user_vals.update({
                'is_operator': True,
                'groups_id': [(6, 0, [self.env.ref('field_service_management.group_operator').id])],
            })
        elif self.is_manager:
            user_vals.update({
                'is_manager': True,
                'groups_id': [(6, 0, [self.env.ref('field_service_management.group_fsm_manager').id])],
            })
        # Creating User Record.
        user_rec = self.env['res.users'].sudo().create(user_vals)
        # set the email address in res partner model
        user_rec.partner_id.sudo().write({
                'email' : self.work_email,
                'partner_user_id': user_rec.id
                })
        # Set the related user in employee
        self.user_id = user_rec.id
        return user_rec

    @api.multi
    def open_user(self):
        """
        This Method is used to Open User from employee record.
        @param self: The object pointer
        """
        # Created res users in open
        context = dict(self._context or {})
        return {
            'view_type': 'form',
            'view_id': self.env.ref('base.view_users_form').id,
            'view_mode': 'form',
            'res_model': 'res.users',
            'res_id': self.user_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
        }

    @api.multi
    def get_serviceman_details(self, user_id):
        employee_rec = self.env['hr.employee'].sudo().search([('user_id', '=', int(user_id))], limit=1)
        if employee_rec:
            user_vals = {
                'name': employee_rec.name,
                'phone': employee_rec.work_phone,
                'email': employee_rec.work_email,
                'image': employee_rec.image,
                'employee_id': employee_rec.id
            }
        else:
            user_rec = self.env['res.users'].sudo().browse([int(user_id)])
            if user_rec:
                user_vals = {
                    'name': user_rec.name,
                    'phone': user_rec.phone,
                    'email': user_rec.email,
                    'image': user_rec.image,
                }
        return user_vals
