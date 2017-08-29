# -*- coding: utf-8 -*-
import werkzeug.utils
from odoo import http
from odoo.http import request


class QueueManagement(http.Controller):
    @http.route('/queue/screen/', auth='public')
    def index(self, **kw):
        branch_id = int(kw.get('branch_id'))
        branch = request.env['queue.management.branch'].sudo().browse(branch_id)
        values = {
            'branch': branch,
        }
        return http.request.render('queue_management.queue_screen', values)

    @http.route('/queue/new_ticket/', auth='public')
    def new_ticket(self, **kw):
        service_id = int(kw.get('service_id'))
        service = request.env['queue.management.service'].sudo().browse(service_id)
        service.new_ticket()
        return werkzeug.utils.redirect('/queue/screen?branch_id={}'.format(service.branch_id.id))
