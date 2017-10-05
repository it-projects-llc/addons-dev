# -*- coding: utf-8 -*-
import werkzeug.utils
from odoo import http
from odoo.http import request


class QueueManagement(http.Controller):
    @http.route('/queue/services/', auth='public')
    def service(self, **kw):
        branch_id = int(kw.get('branch_id'))
        branch = request.env['queue.management.branch'].sudo().browse(branch_id)
        values = {
            'branch': branch,
        }
        return http.request.render('queue_management.queue_service', values)

    @http.route('/queue/new_ticket/', auth='public')
    def new_ticket(self, **kw):
        service_id = int(kw.get('service_id'))
        service = request.env['queue.management.service'].sudo().browse(service_id)
        service.new_ticket()
        return werkzeug.utils.redirect('/queue/services?branch_id={}'.format(service.branch_id.id))

    @http.route('/queue/screen/', auth='public')
    def screen(self, **kw):
        branch_id = int(kw.get('branch_id'))
        branch = request.env['queue.management.branch'].sudo().browse(branch_id)
        log_records = request.env['queue.management.log'].sudo().search([('ticket_state', '=', 'current'),
                                                                         ('service_id.branch_id', '=', branch.id)])
        print '\n\n\n', log_records, '\n\n\n'
        values = {
            'branch': branch,
            'log_records': log_records,
        }
        return http.request.render('queue_management.queue_screen', values)
