# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import json
import urllib
from datetime import datetime
from odoo import api, fields, models, _,SUPERUSER_ID
from odoo.exceptions import ValidationError, Warning, except_orm

class Job(models.Model):
    _inherit = 'project.task'
    _order = 'create_date desc'

    job_sequence = fields.Char(
        string='Job Sequence',
        help="Gives the sequence order when displaying a list of jobs.")
    project_id = fields.Many2one('project.project',
                                 string='Service',
                                 default=lambda self: self.env.context.get(
                                     'default_project_id'),
                                 index=True,
                                 required="1",
                                 track_visibility='onchange',
                                 change_default=True,
                                 help='This field is a basically\
                                     Service skill for Serviceman.')
    street = fields.Char(
        string='Street')
    street2 = fields.Char(
        string='Street2')
    area_id = fields.Many2one(
        comodel_name='area.area',
        string='Area Name',
        help='The name of the area.')
    zip = fields.Char(
        string='Zip',
        change_default=True,
        help='The name of the zip code.')
    city_id = fields.Many2one(
        comodel_name='city.city',
        string='City',
        help='The name of the city.')
    state_id = fields.Many2one(
        comodel_name='res.country.state',
        string='State',
        help='The name of the state.')
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country',
        help='The name of the country.')
    zone_id = fields.Many2one(
        comodel_name='zone.zone',
        string='Zone Name',
        help='The name of the zone.')
    site_cross_street = fields.Text('Site Cross Street')
    same_as_above = fields.Boolean('Same as above')

    formatted_address = fields.Char(
        string='Billing Address',
        help='Display Formatted address')
    bil_street2 = fields.Char(
        string='Street2')
    bil_area_id = fields.Many2one(
        comodel_name='area.area',
        string='Area Name',
        help='The name of the area.')
    bil_zip = fields.Char(
        string='Zip',
        change_default=True,
        help='The name of the zip code.')
    bil_city_id = fields.Many2one(
        comodel_name='city.city',
        string='City',
        help='The name of the city.')
    bil_state_id = fields.Many2one(
        comodel_name='res.country.state',
        string='State',
        help='The name of the state.')
    bil_country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country',
        help='The name of the country.')
    bil_zone_id = fields.Many2one(
        comodel_name='zone.zone',
        string='Zone Name',
        help='The name of the zone.')
    phone = fields.Char(
        string='Work Phone')
    latitude = fields.Float(
        string='Latitude',
        digits=(16, 8),
        help='Latitude of the place.')
    longitude = fields.Float(
        string='Longitude',
        digits=(16, 8),
        help='Longitude of the place.')
    order_line_ids = fields.One2many(
        comodel_name='job.line',
        inverse_name='job_id',
        string='Job Line',
        help='create the product name,price and quantity')





    feedback_line_ids = fields.One2many(
        comodel_name='job.feedback',
        inverse_name='task_id',
        string='Feedback',
        help='Links all the feedback received for the job.')
    priority = fields.Selection(
        selection=[('0', 'Normal'),
                   ('1', 'High')],
        string='Priority',
        default='0',
        index=True,
        help='Normal and High Priority of the Jobs.')
    jobs_rejected = fields.Boolean(
        string='Rejected Job',
        help='If checked the job is rejected.')
    rejected_reason = fields.Char(
        string='Reject reason',
        help='Reason for job rejection.')
    is_express_service = fields.Boolean(
        string='Express service',
        help='This field True Extra charges add in job lines')
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice',
        copy=False,
        help='This field invisible but create\
            invoice to visible field invoice.')
    signature = fields.Binary(
        string='Signature',
        help='Click on signature widget open.')
    schedule_date = fields.Datetime(
        string='Schedule on',
        copy=False,
        help='Current system Datetime display.')
    # plan_hours = fields.float(string='Planned Hours')
    timesheet_count = fields.Integer(
        compute='_compute_timesheet_count',
        string="Timesheet",
        help='if Display the Timesheet Count\
            for the Jobs Kanban view.')
    date_deadline = fields.Datetime(string='Deadline', index=True, copy=False,
                                    help='Display Jobs Deadline date')
    state = fields.Selection(selection=[('draft', 'New'),
                              ('reserved', 'Reserved'),
                              ('scheduled', 'Scheduled'),
                              ('open', 'In Progress'),
                              ('done', 'Complete'),
                              ('invoiced', 'Invoiced'),
                              ('partial', 'Partially Complete'),
                              ('cancelled', 'Cancelled')],
                             string='State',
                             related='stage_id.state',
                             help='Which type state select base on scenario',
                             store=True)
    feedback_count = fields.Integer(
        compute='_compute_feedback_count', string='# of Feedback')
    invoice_check=fields.Boolean("invoice")
    site_check=fields.Boolean("Site Visit")


    @api.multi
    def custom_create_invoice(self):
        list=[]
        account_type_id = self.env['account.account.type'].search([('name', '=', 'Receivable')])
        account_id = self.env['account.account'].search([('name', '=', 'Debtors'), ('user_type_id', '=', account_type_id.id)])
        invoice_id=self.env['account.invoice'].create({'partner_id':self.partner_id.id,'account_id':account_id.id,'job_id':self.job_sequence})
        account_type_line_id = self.env['account.account.type'].search([('name', '=', 'Income')])
        account_line_id = self.env['account.account'].search([('name', '=', 'Local Sales'), ('user_type_id', '=', account_type_line_id.id)])

        for line in self.order_line_ids:
            if line.check_box:
                vals={'invoice_id':invoice_id.id,
                    'product_id':line.product_id.id,
                      'quantity':line.product_uom_qty,
                      'price_unit':line.price_unit,
                      'name':line.name,
                       'account_id':account_line_id.id}
                invoice_line_ids = self.env['account.invoice.line'].create(vals)
        stage_id=self.env['project.task.type'].search([('name','=','Complete'),('state','=','done')])
        if stage_id:
            self.stage_id=stage_id.id

        # self.state='done'
        self.invoice_check=True
        #         list.append(vals)
        # for lis in list:

    @api.multi
    def new_job_with_uninstall_products(self,default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = _("%s (site visit)") % self.name
        if 'remaining_hours' not in default:
            default['remaining_hours'] = self.planned_hours
        if not default.get('parent_name'):
            default['parent_name'] = self.id
        duplicate_job = super(Job, self).copy(default)
        uom = self.env['product.uom'].search([('name','=','Unit(s)')]).id
        for lines in self.order_line_ids:
            if not lines.check_box:
                vals={'product_id':lines.product_id.id,
                      'product_uom_qty':lines.product_uom_qty,
                      'name':'[%s]%s' % (lines.product_id.default_code,lines.product_id.name),
                      'price_unit':lines.price_unit,
                      'product_uom':uom}
                duplicate_job.write({'order_line_ids':[(0,0,(vals))],
                                     'site_check':False,
                                     'invoice_check':False})
        self.write({'site_check':True})

    @api.onchange('same_as_above')
    def onchange_same_add(self):
        if self.same_as_above == True:
            self.formatted_address = self.street
            self.bil_street2 = self.street2
            self.bil_area_id = self.area_id.id
            self.bil_city_id = self.city_id.id
            self.bil_state_id = self.state_id.id
            self.bil_zip = self.zip
            self.bil_zone_id = self.zone_id
            self.bil_country_id = self.country_id
        else:
            self.formatted_address = False
            self.bil_street2 = False
            self.bil_area_id = False
            self.bil_city_id = False
            self.bil_state_id = False
            self.bil_zip = False
            self.bil_zone_id = False
            self.bil_country_id = False
    
    @api.multi
    def action_resource_availibility(self):
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        partner_ids = self.env.user.partner_id.ids
        if self.user_id:
            partner_ids.append(self.user_id.partner_id.id)
        action['context'] = {
            'default_partner_id': self.user_id.partner_id.id,
            'search_default_partner_id': self.user_id.partner_id.id,
            'default_partner_ids': partner_ids,
            'search_default_partner_ids': self.user_id.partner_id.name,
        }
        return action

    # Calculate Jobs feedback count
    def _compute_feedback_count(self):
        for task_rec in self:
            task_rec.feedback_count = len(task_rec.feedback_line_ids.ids)

    @api.multi
    def unlink(self):
        """
        This method throw only draft state jobs deleted
        """
        for job_rec in self:
            if job_rec.state in ['pending', 'open', 'done']:
                raise ValidationError(
                    _('''You can only delete draft and cancelled jobs.'''))
        return super(Job, self).unlink()

    @api.multi
    def button_view_feedbacks(self):
        """
        This method throw action open and feedback line create
        """
        return {
            'name': _('Feedbacks'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'job.feedback',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in self.feedback_line_ids])],
        }

    @api.multi
    def action_notify_customer(self):
        """
        This method is used to Notify to Customer using Mail Template.
        """
        # if not select a customer and raise the validation message select a
        # customer
        if not self.partner_id:
            raise ValidationError(
                'Please Select a Customer Assigned to in Notify mail!')
        self.ensure_one()
        template = self.env.ref(
            'field_service_management.notify_customer_jobs_mail_template',
            False)
        ctx = dict(
            default_model='project.task',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
        )
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def action_notify_serviceman(self):
        """
        This method is used to notify to Serviceman by Mail Template
        """
        # if not select a Assigned to and raise the validation message select a
        # Assigned to user
        if not self.user_id:
            raise ValidationError(
                'Please Select a Serviceman Assigned to in Notify mail!')
        self.ensure_one()
        serviceman_template = self.env.ref(
            'field_service_management.notify_serviceman_jobs_mail_template',
            False)
        ctx = dict(
            default_model='project.task',
            default_res_id=self.id,
            default_use_serviceman_template=bool(serviceman_template),
            default_template_id=serviceman_template and
            serviceman_template.id or False,)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def create(self, vals):
        """
        This method is used to Create a Sequence,
        Getting list of Employees with a specific skill
        Getting list of Employees line in a specific area.
        Getting automatic fetch address save the record in jobs view
        """
        vals['job_sequence'] = self.env['ir.sequence'].next_by_code('project')
        # Gettings res company boolean fields true to assign jobs automatically
        if self.env.user.company_id.automatically_assign_jobs:

            # if not select project id raise an validation Error Message
            if not vals.get('project_id'):
                raise ValidationError(
                    'Please mention Service to assign the jobs \
                    Automatically.')
            employee_ids = self.env['emp.skill.line'].sudo().get_employee_by_skill(
                vals['project_id'])
            # if not select area raise an validation Error Message
            if employee_ids:
                if vals.get('area_id'):
                    employee_in_area_ids = self.get_employee_by_area(
                        employee_ids, vals['area_id'])
                    if employee_in_area_ids and employee_in_area_ids[0].user_id:
                        vals.update({
                            'user_id': employee_in_area_ids[0].user_id and
                            employee_in_area_ids[0].user_id.id or False})
                    else:
                        # Employee records browse and update
                        employee_rec = self.env['hr.employee'].browse(
                            [employee_ids[0]])
                        vals.update({
                            'user_id': employee_rec.user_id and
                            employee_rec.user_id.id or False})
                else:
                    # Employee records browse and update
                    employee_rec = self.env['hr.employee'].browse(
                        [employee_ids[0]])
                    vals.update({
                        'user_id': employee_rec.user_id and
                        employee_rec.user_id.id or False})

        # Create a jobs and save the record in new stage select
        # stage_rec = self._get_stage_search()
        # if stage_rec:
        #     vals.update({
        #         'stage_id': stage_rec[0].id
        #     })
        self.env.uid = SUPERUSER_ID
        result = super(Job, self).create(vals)

        # Gettings res company boolean fields true to fetch automatic address
        # fill
        if self.env.user.company_id.automatic_fetch_address:
            result.fetch_address()
        return result

    def get_employee_by_area(self, employee_ids, area):
        """
        Get area in hr_employee model and area wise search in
        action_view_my_job employee
        """
        # search the employee_ids and area_ids
        employee_by_erea_rec = self.env['hr.employee'].search(
            [('id', 'in', employee_ids),
             ('area_ids', 'in', [area])])
        return employee_by_erea_rec

    def get_employee_by_city(self, employee_ids, city):
        """
        Get city in hr_employee model and city wise search in
        action_view_my_job employee
        """
        # search the employee_ids and city_ids
        employee_by_city_rec = self.env['hr.employee'].search(
            [('id', 'in', employee_ids),
             ('city_ids', 'in', [city])])
        return employee_by_city_rec

    @api.model
    def default_get(self, fields):
        """
        Override the default get method
        """
        # create jobs Default getting the user_id and Schedule_date
        res = super(Job, self).default_get(fields)
        res.update({
            'user_id': False,
            'schedule_date': str(datetime.now()),
        })
        return res

    def _get_stage_search(self):
        # search the state in draft
        stage_rec = self.env['project.task.type'].search([(
            'state', '=', 'draft')])
        return stage_rec

    # @api.constrains('schedule_date', 'date_deadline')
    # def _check_dates(self):
    #     if self.date_deadline and self.schedule_date > self.date_deadline:
    #         raise ValidationError('Deadline should be greater than schedule date.')

    @api.multi
    def suggest_best_serviceman(self):
        """
        Suggest best service man in jobs view
        """
        # check the condition select statement
        if not self.area_id or not self.project_id or not self.city_id:
            raise Warning(
                'Please select service, city and area to get the suggestion.')

        # suggest the name and login id for res.users form data
        for job_rec in self:
            job_rec = job_rec.with_context({'job_id': self.id})
            employee_ids = self.env['emp.skill.line'].get_employee_by_skill(
                job_rec.project_id.id)
            user_ids = []

            # get employee record in area wise service person in suggest
            if employee_ids:
                employee_by_area_recs = self.get_employee_by_area(
                    employee_ids, job_rec.area_id.id)
                if employee_by_area_recs:
                    for employee_rec in employee_by_area_recs:
                        if employee_rec.user_id:
                            user_ids.append(employee_rec.user_id.id)

                # get employee record in city wise service person in suggest
                employee_by_city_recs = self.get_employee_by_city(
                    employee_ids, job_rec.city_id.id)
                if employee_by_city_recs:
                    for employee_rec in employee_by_city_recs:
                        if employee_rec.user_id:
                            user_ids.append(employee_rec.user_id.id)
            return {
                'name': 'Suggest Best Service Man',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'res.users',
                'target': 'new',
                'view_id': self.env.ref
                ('field_service_management.view_res_user_tree_inherited').id,
                'domain': [('id', 'in', user_ids)],
                'context': job_rec._context
            }

    # Invoice and product lines prepare
    def prepare_invoice_line(self, product_rec, invoice_rec, journal_id):
        invoice_line = False
        line_values = {}
        line_values = {
            'product_id': product_rec and product_rec.id or False,
            'invoice_id': invoice_rec.id,
        }
        # Initiating a new invoice line record object
        invoice_line = self.env['account.invoice.line'].new(line_values)
        invoice_line._onchange_product_id()
        line_values = invoice_line._convert_to_write(
            {name: invoice_line[name] for name in invoice_line._cache})
        line_values.update(invoice_line.
                           with_context({'journal_id': journal_id}).
                           default_get(invoice_line.default_get(
                               invoice_line._fields)))
        return line_values

    @api.multi
    def create_invoice(self):
        """
        Create Customer invoice in button trough in job view.
        """
        for job_rec in self:
            # Check if Partner, Service and Serviceman exists in the Job
            if not job_rec.partner_id or not job_rec.user_id or not\
                    job_rec.project_id:
                raise Warning(
                    'Please assign Service person,Customer and Service to create \
                    an invoice.')

            # Check if there are timesheet entries and job lines to invoice
            if not job_rec.timesheet_ids and not job_rec.order_line_ids:
                raise Warning(
                    'There are not timesheet entries or job cart \
                    products to invoice.')

            invoice_vals = {}
            invoice_line_list = []

            # Getting Employee record
            employee_rec = self.env['hr.employee'].search([(
                'user_id', '=', job_rec.user_id.id)])
            if len(employee_rec) > 1:
                raise Warning('You cannot have two Employees with\
                    same Related User.')

            # Updating Invoice Vals
            invoice_vals.update({
                'partner_id': job_rec.partner_id.id,
            })

            # Initiating a new invoice record object
            invoice_new = self.env['account.invoice'].new(invoice_vals)

            # Calling the default_get method of Invoice
            invoice_vals.update(invoice_new.default_get(invoice_new._fields))

            # Check if the Journal exists.
            if not invoice_vals.get('journal_id'):
                raise Warning(
                    'Please configure chart of accounts.')

            # Updating Invoice Vals
            invoice_vals.update({
                'user_id': job_rec.user_id.id,
            })
            # Create the Invoice
            invoice_rec = self.env['account.invoice'].create(invoice_vals)

            # Looping on Job lines
            for job_line in job_rec.order_line_ids:
                line_values = self.prepare_invoice_line(
                    job_line.product_id, invoice_rec, invoice_vals.
                    get('journal_id'))
                line_values.update({
                    'quantity': job_line.product_uom_qty,
                    'price_unit': job_line.price_unit,
                    'job_id': job_line.id,
                })
                invoice_line_list.append(
                    (0, 0, line_values))

            # Calculating the number of hours worked
            total_work_hours = 0
            if job_rec.timesheet_ids:

                # Get Service Rate for hr employee
                rate = 0
                if job_rec.is_express_service:
                    rate = self.env[
                        'emp.skill.line'].get_express_rate_for_skill(
                        employee_rec[0].id, job_rec.project_id.id)
                else:
                    rate = self.env[
                        'emp.skill.line'].get_rate_for_skill(
                        employee_rec[0].id, job_rec.project_id.id)
                for timesheet_line in job_rec.timesheet_ids:
                    total_work_hours += timesheet_line.unit_amount
            if total_work_hours:
                line_values = self.prepare_invoice_line(
                    False, invoice_rec, invoice_vals.get('journal_id'))
                line_values.update({
                    'name': 'Service Charge',
                    'quantity': total_work_hours,
                    'price_unit': rate
                })
                invoice_line_list.append(
                    (0, 0, line_values))

            # Writing the invoice lines
            invoice_rec.write({'invoice_line_ids': invoice_line_list})

            # Writing the new created invoice_id to the Jobs.
            job_rec.write({
                'invoice_id': invoice_rec.id
            })
        return True

    @api.multi
    def open_invoice(self):
        """
        This Method is used to Open invoice from maintenance record.
        @param self: The object pointer
        """
        # Created invoice lines open
        context = dict(self._context or {})
        wiz_form_id = self.env['ir.model.data'].get_object_reference(
            'account', 'invoice_form')[1]
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'res_id': self.invoice_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
        }

    @api.multi
    def _compute_timesheet_count(self):
        """
        Timesheet count for len Function throw integer value.
        """
        # count the kanban view for timesheet lines
        for Job in self:
            Job.timesheet_count = len(Job.timesheet_ids)

    @api.multi
    def action_set_active(self):
        """
        Display the Active record in job kanban view
        """
        return self.write({'active': True})

    @api.multi
    def action_set_unactive(self):
        """
        Display the Unactive record in job kanban view
        """
        return self.write({'active': False})

    @api.multi
    def fetch_address(self):
        """
        This Button method is used to click 
        according fields values and latlang to address
        Found.
        """
        # Googleapis url for json data and get latlng to address
        url = 'http://maps.googleapis.com/maps/api/geocode/json?latlng='
        url += urllib.quote(str(self.latitude).encode('utf8')) + \
            ',' + urllib.quote(str(self.longitude).encode('utf8'))
        result = json.load(urllib.urlopen(url))
        map_result_data = result.get('results')

        # Looping on address data
        if map_result_data:
            address_data = map_result_data[0].get('address_components')
            formatted_address = map_result_data[0].get('formatted_address')
            if address_data:
                # Looping on Country or Search and Create a Record in
                # res.country
                for place_details in address_data:
                    if 'country' in place_details.get('types'):
                        country_rec = self.env['res.country'].search(
                            [('code', '=', place_details.get('short_name'))])
                        if country_rec:
                            self.country_id = country_rec.id
                        else:
                            country_rec = self.env['res.country'].create(
                                {'name': place_details.get('long_name'),
                                 'code': place_details.get('short_name')})
                            self.country_id = country_rec.id

                # Looping on State or Search and Create a Record in
                # res.country.state
                for place_details in address_data:
                    if 'administrative_area_level_1' in place_details.\
                            get('types'):
                        state_rec = self.env['res.country.state'].search(
                            [('name', 'ilike', place_details.
                                get('long_name'))])
                        if state_rec:
                            self.state_id = state_rec.id
                        else:
                            create_state_id = self.env['res.country.state'].\
                                create({'name': place_details.get('long_name'),
                                        'code': place_details.
                                        get('short_name'),
                                        'country_id': self.country_id.id})
                            self.state_id = create_state_id.id

                # Looping on City or Search and Create a Record in city.city
                for place_details in address_data:
                    if 'administrative_area_level_2' in place_details.\
                            get('types'):
                        city_rec = self.env['city.city'].search(
                            [('name', 'ilike', place_details.
                                get('long_name'))])
                        if city_rec:
                            self.city_id = city_rec.id
                        else:
                            create_city_rec = self.env['city.city'].\
                                create({'name': place_details.get('long_name'),
                                        'state_id': self.state_id.id})
                            self.city_id = create_city_rec.id

                # Looping on Street and Zip or Search and Create Record
                for place_details in address_data:
                    if 'route' in place_details.get('types'):
                        self.street = place_details.get('long_name')
                    if 'postal_code' in place_details.get('types'):
                        self.zip = place_details.get('long_name')
                    if 'locality' in place_details.get('types'):
                        self.street2 = place_details.get('long_name')

                    # Add formatted address map result data
                    self.formatted_address = formatted_address
        if result['status'] != 'OK':
            return None
        return True


class JobLine(models.Model):
    _name = 'job.line'
    _inherit = 'sale.order.line'

    job_id = fields.Many2one(
        comodel_name='project.task',
        string='Job',
        help='This field is a related to jobs view in create a jobs')
    check_box=fields.Boolean("checked")
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Order Reference',
        required=False,
        help='This field is a sale order reference field')

