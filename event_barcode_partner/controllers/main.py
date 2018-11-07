# -*- coding: utf-8 -*-
from odoo import fields, http, _
from odoo.http import request
from odoo.addons.event_barcode.controllers.main import EventBarcode
import json


class EventBarcodeExtended(EventBarcode):

    def compound_vals(self, attendees):
        return [{
            'a_name': a.name,
            'p_name': a.partner_id.name,
            'state': a.state,
            'aid': a.id,
            'rfid': a.rfid,
            'signed_terms': a.signed_terms,
        } for a in attendees]

    @http.route('/event_barcode/get_attendees_by_name', type='json', auth="user")
    def get_attendees_by_name(self, event_id, name, **kw):
        Registration = request.env['event.registration']
        attendees = Registration.search([('event_id', '=', event_id),
                                         ('name', 'ilike', name)])
        return self.compound_vals(attendees)

    @http.route('/event_barcode/get_attendee_by_barcode', type='json', auth="user")
    def get_attendee_by_barcode(self, event_id, barcode, **kw):
        Registration = request.env['event.registration']
        attendees = Registration.search([('event_id', '=', event_id),
                                         ('barcode', '=', barcode)], limit=1)
        return self.compound_vals(attendees)

    @http.route('/event_barcode/set_rfid', type='json', auth="user")
    def set_attendee_rfid(self, rfid, aid, **kw):
        Registration = request.env['event.registration']
        attendee = Registration.browse(aid)

        attendee.write({
            'rfid': rfid
        })

        return self.compound_vals(attendee)

    @http.route('/event_barcode/register_attendee', type='json', auth="user")
    def register_attendee(self, barcode, event_id, **kw):
        Registration = request.env['event.registration']
        attendee = Registration.search([('barcode', '=', barcode), ('event_id', '=', event_id)], limit=1)

        if not attendee:
            return {'warning': _('This ticket is not valid for this event')}
        count = Registration.search_count([('state', '=', 'done'), ('event_id', '=', event_id)])
        attendee_name = attendee.name or _('Attendee')
        if attendee and attendee.state in ['open', 'draft'] and not attendee.signed_terms:
            return {'warning': _('%s did not signed terms') % attendee_name, 'count': count}

        return super(EventBarcodeExtended, self).register_attendee()

    @http.route('/event_barcode/register_attendee_by_id', type='json', auth="user")
    def register_attendee_by_id(self, attendee_id, **kw):
        Registration = request.env['event.registration']
        attendee = Registration.browse(int(attendee_id))
        if not attendee:
            return {'warning': _('This ticket is not valid for this event')}
        count = Registration.search_count([('state', '=', 'done'), ('event_id', '=', attendee.event_id.id)])
        attendee_name = attendee.name or _('Attendee')

        if attendee.state == 'cancel':
            return {'warning': _('Canceled registration'), 'count': count, 'attendee': self.compound_vals(attendee)}
        elif attendee.state != 'done':
            attendee.write({'state': 'done', 'date_closed': fields.Datetime.now()})
            count += 1
            return {'success': _('%s is successfully registered') % attendee_name, 'count': count, 'attendee': self.compound_vals(attendee)}
        else:
            return {'warning': _('%s is already registered') % attendee_name, 'count': count, 'attendee': self.compound_vals(attendee)}


    @http.route('/event_barcode/sign_request', type="json", auth="user")
    def update_connection(self, attendee_id, event_id, barcode_interface_id):
        channel_name = "est.longpolling.sign"
        event_id = request.env['event.event'].browse(event_id)
        if request.env['ir.config_parameter'].get_param('pos_longpolling.allow_public'):
            event_id = event_id.sudo()

        attendee = request.env["event.registration"].browse(int(attendee_id))
        sign_req = attendee.event_request_id

        if not sign_req:
            sign_req = request.env["signature.request"].create({
                'template_id': attendee.event_id.signature_template_id.id,
                'attendee': attendee.id,
                'reference': 'Event Terms ' + attendee.name
            })
            attendee.event_request_id = sign_req.id

        data = {
            'sign_token': sign_req.access_token,
            'rid': sign_req.id,
            'attendee_name': attendee.name,
            'attendee_id': attendee.id,
        }

        res = event_id.send_to_all_estes(channel_name, barcode_interface_id, json.dumps(data))
        return res

    @http.route('/event_barcode/new_session', type="json", auth="user")
    def new_barcode_interface(self, event_id):
        param_model = request.env['ir.config_parameter'].sudo()
        params = param_model.get_param('event_barcode.' + str(event_id) + '.sessions')
        if not params:
            params = json.dumps(0)
        param = json.loads(params)
        new_param = int(float(param)) + 1
        param_model.set_param('event_barcode.' + str(event_id) + '.sessions', json.dumps(new_param))

        return new_param

    @http.route('/event_barcode/submit_sign', type="json", auth="user")
    def submit_kiosk_sign(self, attendee_id, sign, barcode_interface_id):
        Registration = request.env['event.registration']
        ir_attachment = request.env['ir.attachment']

        attendee = Registration.browse(attendee_id)

        attachment = ir_attachment.create({
            'type': 'binary',
            'name': attendee.name + 'E-Sign',
            'datas': sign,
            'datas_fname': attendee.name + 'E-Sign',
            'res_id': attendee.id,
            'res_model': "event.registration",
        })

        attendee.write({
            'sign_attachment_id': attachment.id,
        })

        # attendee.embed_sign_to_pdf()

        channel_name = "bi.longpolling.notifs"
        attendee.event_id.send_to_barcode_interface(channel_name, barcode_interface_id, json.dumps(self.compound_vals(attendee)))

        return attendee.id
