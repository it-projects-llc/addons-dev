# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
import json


class UserController(http.Controller):

    @http.route(['/create_user'], type='json', auth="public", website=True,
                csrf=False)
    def res_users(self, **kwargs):
        users_data_dic = kwargs.get('kwargs')
        result = json.loads(users_data_dic.get('services'))
        services_data = result
        vals = {}
        group_ids = []
        if users_data_dic.get('is_serviceman'):
            vals.update({
                'name': users_data_dic.get('customer_name'),
                'work_email': users_data_dic.get('customer_email'),
                'work_phone': users_data_dic.get('contact'),
                'is_serviceman': True,
            })
            service_list = []
            if services_data:
                for service in services_data:
                    service_list.append((0, 0, service))
            if service_list:
                vals.update({
                    'emp_skill_ids': service_list
                })
            employee_rec = request.env['hr.employee'].sudo().create(vals)
            users_rec = employee_rec.create_user(
                password=users_data_dic.get('default_password'))
        else:
            customer_group_rec = request.env['ir.model.data'].\
                sudo().get_object(
                'field_service_management', 'group_customer')
            group_ids.append(customer_group_rec.id)

            vals.update({
                'name': users_data_dic.get('customer_name'),
                'login': users_data_dic.get('customer_email'),
                'password': users_data_dic.get('default_password'),
                'mobile': users_data_dic.get('contact'),
                'groups_id': [(6, 0, group_ids)],
                'customer': True,
            })
            users_rec = request.env['res.users'].sudo().create(vals)
            # set the email address from android apps create the user
            users_rec.partner_id.sudo().write({
                'email' : users_data_dic.get('customer_email'),
                'partner_user_id': users_rec.id
                })
        return str(users_rec.id)

    @http.route(['/get_services'], type='json', auth="public", website=True,
                csrf=False)
    def project_project(self, **kwargs):
        service_vals = {}
        project_rec = request.env['project.project'].sudo().search(
            [('is_available_for_service', '=', True)])
        service_list = []
        for services in project_rec:
            service_dict = {'id': services.id,
                            'name': services.name}
            service_list.append(service_dict)
        return service_list
