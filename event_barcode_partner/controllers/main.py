# -*- coding: utf-8 -*-
from odoo import fields, http, _
from odoo.http import request
from odoo.addons.event_barcode.controllers.main import EventBarcode
import json
import datetime


class EventBarcodeExtended(EventBarcode):

    def compound_vals(self, attendees, event_id):
        return {
            'attendees': [{
                'a_name': a.name,
                'p_name': a.partner_id.name,
                'state': a.state,
                'aid': a.id,
                'rfid': a.rfid,
                'signed_terms': a.signed_terms,
            } for a in attendees],
            'bracelets': self.get_bracelet_info(event_id)
        }

    def get_bracelet_info(self, event_id):
        event = request.env['event.event'].browse(event_id)
        tickets = event.event_ticket_ids
        today = datetime.datetime.now()
        attendees = request.env['event.registration'].search([('event_ticket_id', 'in', tickets.ids),
                                                              ('state', '=', 'done')])
        vals = []
        for t in tickets:
            done_attendees = attendees.filtered(lambda x: x.event_ticket_id.id == t.id)
            done_today = done_attendees.filtered(lambda x:
                                                 datetime.datetime.strptime(x.date_closed, '%Y-%m-%d %H:%M:%S').day == today.day
                                                 )
            done_hour = done_today.filtered(lambda x:
                                            datetime.datetime.strptime(x.date_closed, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=1) <=
                                            datetime.datetime.strptime(x.date_closed, '%Y-%m-%d %H:%M:%S') <=
                                            datetime.datetime.strptime(x.date_closed, '%Y-%m-%d %H:%M:%S')
                                            )

            vals.append({
                'id': t.id,
                'ticket_name': t.name,
                'done_hour': done_hour and len(done_hour) or 0,
                'done_today': done_today and len(done_today) or 0,
                'done_attendees': done_attendees and len(done_attendees) or 0,
            })
        return vals

    # def read_group_done_attendees(self, event_id, additional_domain):
    #     event = request.env['event.event'].browse(event_id)
    #     domain = additional_domain + [('event_ticket_id', 'in', event.event_ticket_ids.ids), ('state', '=', 'done')]
    #     registration = request.env['event.registration']
    #     return registration.read_group(domain, ['event_ticket_id'], ['event_ticket_id'])
    #
    # def get_bracelet_info(self, event_id):
    #     done_attendees = self.read_group_done_attendees(event_id, [])
    #     today = datetime.datetime.now()
    #     done_today = self.read_group_done_attendees(event_id, [('date_closed.day', '=', today.day)])
    #     done_hour = self.read_group_done_attendees(event_id, [('date_closed.day', '<=', today.hour),
    #                                                           ('date_closed.day', '>=', today.hour - 1)])
    #     return {
    #         'done_hour': len(done_hour),
    #         'done_today': len(done_today),
    #         'done_attendees': len(done_attendees),
    #     }


    @http.route()
    def get_event_data(self, event_id):
        res = super(EventBarcodeExtended, self).get_event_data(event_id)
        res['bracelets'] = self.get_bracelet_info(event_id)
        res['event_id'] = event_id

        url_first_part = request.env['ir.config_parameter'].get_param('web.base.url') + "/web#id="
        url_second_part = "&view_type=form&model=event.registration"
        res['attendee_url'] = [url_first_part, url_second_part]
        res['rfid_templates'] = request.env['event.event'].browse(event_id).rfid_templates

        return res

    @http.route('/event_barcode/get_attendees_by_name', type='json', auth="user")
    def get_attendees_by_name(self, event_id, name, **kw):
        Registration = request.env['event.registration']
        attendees = Registration.search([('event_id', '=', event_id),
                                         ('name', 'ilike', name)])
        return self.compound_vals(attendees, event_id)

    @http.route('/event_barcode/get_attendee_by_barcode', type='json', auth="user")
    def get_attendee_by_barcode(self, event_id, barcode, **kw):
        Registration = request.env['event.registration']
        attendees = Registration.search([('event_id', '=', event_id),
                                         ('barcode', '=', barcode)], limit=1)
        return self.compound_vals(attendees, event_id)

    @http.route('/event_barcode/set_rfid', type='json', auth="user")
    def set_attendee_rfid(self, rfid, aid, **kw):
        Registration = request.env['event.registration']
        attendee = Registration.browse(aid)

        attendee.write({
            'rfid': rfid
        })

        return self.compound_vals(attendee, attendee.event_id.id)

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
            return {'warning': _('This ticket is not valid for this event'), 'data': False}
        count = Registration.search_count([('state', '=', 'done'), ('event_id', '=', attendee.event_id.id)])
        attendee_name = attendee.name or _('Attendee')

        if attendee.state == 'cancel':
            return {'warning': _('Canceled registration'), 'count': count, 'data': self.compound_vals(attendee, attendee.event_id.id)}
        elif attendee.state != 'done':
            attendee.write({'state': 'done', 'date_closed': fields.Datetime.now()})
            count += 1
            return {'success': _('%s is successfully registered') % attendee_name, 'count': count, 'data': self.compound_vals(attendee, attendee.event_id.id)}
        else:
            return {'warning': _('%s is already registered') % attendee_name, 'count': count, 'data': self.compound_vals(attendee, attendee.event_id.id)}

    @http.route('/event_barcode/sign_request', type="json", auth="user")
    def sign_request(self, attendee_id, event_id, barcode_interface_id):
        channel_name = "est.longpolling.sign"
        event_id = request.env['event.event'].browse(event_id)
        if request.env['ir.config_parameter'].get_param('pos_longpolling.allow_public'):
            event_id = event_id.sudo()

        attendee = request.env["event.registration"].browse(int(attendee_id))
        sign_req = attendee.event_request_id
        if not sign_req:
            if not attendee.event_id.signature_template_id:
                channel_name = "bi.longpolling.notifs"
                return attendee.event_id.send_to_barcode_interface(channel_name, barcode_interface_id, json.dumps(
                    {
                        'notification': {
                            'type': 'error',
                            'header': 'Event Signature Template Error',
                            'text': 'Set Event Signature Template before sending requests',
                        }
                    }
                ))

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

        # embed_sign_to_pdf returns false if smth's wrong
        is_embedded = attendee.embed_sign_to_pdf()

        result = self.compound_vals(attendee, attendee.event_id.id)
        result['notification'] = {
            'type': 'success',
            'header': 'Terms Are Signed',
            'message': '',
        }
        if not is_embedded:
            result['notification'] = {
                'type': 'error',
                'header': 'Something went wrong',
                'message': 'PDF is not created, Sing is saved',
            }

        channel_name = "bi.longpolling.notifs"
        attendee.event_id.send_to_barcode_interface(channel_name, barcode_interface_id, json.dumps(result))

        return attendee.id\

    # @http.route('/event_barcode/go_to_attendee_form', type="json", auth="user")
    # def redirect_to_attendee(self, attendee_id):
    #
    #     first_url = request.env['ir.config_parameter'].get_param('web.base.url')
    #     second_url = base_url + "/web#id=" + str(attendee_id) + "&view_type=form&model=event.registration"
    #     return []
