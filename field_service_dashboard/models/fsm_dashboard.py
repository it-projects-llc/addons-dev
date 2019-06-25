# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Serpent Consulting Services Pvt. Ltd.
#    Copyright (C) 2017 OpenERP SA (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models


class FsmDashboard(models.Model):
    _name = 'fsm.dashboard'
    _description = "Fsm Dashboard"

    name = fields.Char("Name")

    @api.model
    def get_fsm_dashboard_details(self):
        """
        Dynamic Dashboard count the jobs and invoices for records
        """
        user_rec = self.env.user
        is_field_service_manager = self.user_has_groups(
            'field_service_management.group_fsm_manager')
        is_field_service_customer = self.user_has_groups(
            'field_service_management.group_customer')
        is_field_service_serviceman = self.user_has_groups(
            'field_service_management.group_serviceman')
        is_field_service_operator = self.user_has_groups(
            'field_service_management.group_operator')
        job_count_id = self.env['project.task'].search_count(
            [('user_id', '=', user_rec.id)])
        customer_job_count_id = self.env['project.task'].search_count([])
        unassigned_job_count_id = self.env['project.task'].search_count(
            [('user_id', '=', False)])
        rejected_job_count_id = self.env['project.task'].search_count(
            [('jobs_rejected', '=', True)])
        customer_invoice_count_id = self.env['account.invoice'].search_count(
                                            [])
        customer_open_invoice_count_id = self.env[
            'account.invoice'].search_count(
            [('state', 'in', ('open', 'pro-forma'))])
        data = {
            'customer_invoice_count_id': customer_invoice_count_id,
            'job_count_id': job_count_id,
            'customer_job_count_id': customer_job_count_id,
            'unassigned_job_count_id': unassigned_job_count_id,
            'rejected_job_count_id': rejected_job_count_id,
            'customer_open_invoice_count_id': customer_open_invoice_count_id,
            'is_field_service_manager': is_field_service_manager,
            'is_field_service_customer': is_field_service_customer,
            'is_field_service_serviceman': is_field_service_serviceman,
            'is_field_service_operator': is_field_service_operator}
        return data
