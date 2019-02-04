# -*- coding: utf-8 -*-
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
import logging
import uuid
import StringIO
import base64
from odoo.exceptions import UserError
from reportlab.lib.utils import ImageReader
from pyPdf import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas

import logging

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    ask_attendees_for_esign = fields.Boolean(string='Attendee E-Sign', compute='_compute_terms_to_sign', readonly=True,
                                             default=False, help='Ask Attendees to Sign before they attendeed')
    terms_to_sign = fields.Char(compute='_compute_terms_to_sign', store=True)

    @api.multi
    @api.depends('pos_event_id')
    @api.onchange('pos_event_id')
    def _compute_terms_to_sign(self):
        for conf in self:
            conf.terms_to_sign = conf.pos_event_id and conf.pos_event_id.terms_to_sign or conf.terms_to_sign or ''
            conf.ask_attendees_for_esign = conf.pos_event_id and conf.pos_event_id.mandatory_esign or False


class EventRegistration(models.Model):
    """Attendee"""
    _inherit = 'event.registration'

    sign_attachment_id = fields.Many2one('ir.attachment', 'E-Sign')
    completed_document = fields.Binary(readonly=True, string="Completed Document", attachment=True)
    signed_terms = fields.Boolean('Terms are Signed', compute='_compute_signed_terms')

    signature_request_id = fields.Many2one('signature.request', string='Terms sign request')

    @api.multi
    @api.depends('sign_attachment_id')
    def _compute_signed_terms(self):
        # TODO: make the check according to the document completion, not only its presence
        for r in self:
            r.signed_terms = bool(r.completed_document)

    @api.one
    def send_term_request(self):
        sign_req = self.env['signature.request']
        requests = sign_req.search([('attendee_id', '=', self.id),
                                    ('template_id', '=', self.event_id.signature_template_id.id)])
        if not len(requests):
            self.env['signature.request'].create({
                'template_id': self.event_id.signature_template_id.id,
                'reference': self.name + self.event_id.name,
                'follower_ids': (6, 0, [self.partner_id]),
                'attendee_id': self.id,
            })

    @api.one
    def embed_sign_to_pdf(self):
        if not self.event_id.signature_template_id:
            return False
        packet = StringIO.StringIO()
        can = canvas.Canvas(packet)
        pdf = self.signature_request_id.template_id or self.event_id.signature_template_id
        itemsByPage = pdf.signature_item_ids.getByPage()
        old_pdf = PdfFileReader(StringIO.StringIO(base64.b64decode(self.event_id.signature_template_id.attachment_id.datas)))
        for p in range(0, old_pdf.getNumPages()):
            if (p+1) not in itemsByPage:
                can.showPage()
                continue
            items = itemsByPage[p + 1]
            for item in items:
                value = self.sign_attachment_id
                if not value:
                    continue

                # value = value.value
                box = old_pdf.getPage(p).mediaBox
                width = int(box.getUpperRight_x())
                height = int(box.getUpperRight_y())
                if item.type_id.type == "signature" or item.type_id.type == "initial":
                    img = base64.b64decode(value.datas[value.datas.find(',') + 1:])
                    can.drawImage(ImageReader(StringIO.StringIO(img)), width*item.posX, height*(1-item.posY-item.height), width*item.width, height*item.height, 'auto', True)
            can.showPage()
        can.save()
        item_pdf = PdfFileReader(packet)
        new_pdf = PdfFileWriter()

        for p in range(0, old_pdf.getNumPages()):
            page = old_pdf.getPage(p)
            page.mergePage(item_pdf.getPage(p))
            new_pdf.addPage(page)

        output = StringIO.StringIO()
        new_pdf.write(output)
        self.completed_document = base64.b64encode(output.getvalue())
        output.close()

        return True

    @api.multi
    def redirect_to_attendee(self, attendee_id):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        record_url = base_url + "/web#id=" + str(attendee_id) + "&view_type=form&model=event.registration"
        client_action = {
            'type': 'ir.actions.act_url',
            'name': "Attendee",
            'target': 'new',
            'url': record_url,
        }

        return client_action


class EventEvent(models.Model):
    """Event"""
    _inherit = 'event.event'

    mandatory_esign = fields.Boolean('Ask for E-Sign', default=True)
    signature_template_id = fields.Many2one('signature.request.template', string='Terms template')
    terms_to_sign = fields.Char(string='Event Terms')
    # rfid_templates = fields.Char(string='RFID Templates', help='Write it in the next way: 057 or 057,056,067')


class SignatureRequest(models.Model):
    _inherit = "signature.request"

    attendee_id = fields.Many2one('event.registration', string="Attendee")
