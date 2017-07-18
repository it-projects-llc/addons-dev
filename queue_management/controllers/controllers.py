# -*- coding: utf-8 -*-
from odoo import http

# class QueueManagement(http.Controller):
#     @http.route('/queue_management/queue_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/queue_management/queue_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('queue_management.listing', {
#             'root': '/queue_management/queue_management',
#             'objects': http.request.env['queue_management.queue_management'].search([]),
#         })

#     @http.route('/queue_management/queue_management/objects/<model("queue_management.queue_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('queue_management.object', {
#             'object': obj
#         })