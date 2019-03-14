# -*- coding: utf-8 -*-
# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api
import logging
from io import StringIO, BytesIO
import base64
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas

import logging

_logger = logging.getLogger(__name__)


class PosEventTicket(models.Model):
    _inherit = 'pos.event.ticket'

    ask_attendees_for_esign = fields.Boolean(string='Attendee E-Sign', default=False, help='Ask Attendees to Sign before they attendeed')


def _fix_image_transparency(image):
    """ Modify image transparency to minimize issue of grey bar artefact.

    When an image has a transparent pixel zone next to white pixel zone on a
    white background, this may cause on some renderer grey line artefacts at
    the edge between white and transparent.

    This method sets transparent pixel to white transparent pixel which solves
    the issue for the most probable case. With this the issue happen for a
    black zone on black background but this is less likely to happen.
    """
    pixels = image.load()
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            if pixels[x, y] == (0, 0, 0, 0):
                pixels[x, y] = (255, 255, 255, 0)


class EventRegistration(models.Model):
    """Attendee"""
    _inherit = 'event.registration'

    sign_attachment_id = fields.Many2one('ir.attachment', 'E-Sign')
    completed_document = fields.Binary(readonly=True, string="Completed Document", attachment=True)
    signed_terms = fields.Boolean('Terms are Signed', compute='_compute_signed_terms')

    signature_request_id = fields.Many2one('sign.request', string='Terms sign request')

    @api.multi
    @api.depends('sign_attachment_id')
    def _compute_signed_terms(self):
        # TODO: make the check according to the document completion, not only its presence
        for r in self:
            r.signed_terms = bool(r.completed_document)

    @api.one
    def send_term_request(self):
        sign_req = self.env['sign.request']
        requests = sign_req.search([('attendee_id', '=', self.id),
                                    ('template_id', '=', self.event_id.signature_template_id.id)])
        if not len(requests):
            self.env['sign.request'].create({
                'template_id': self.event_id.signature_template_id.id,
                'reference': self.name + self.event_id.name,
                'follower_ids': (6, 0, [self.partner_id]),
                'attendee_id': self.id,
            })

    @api.one
    def embed_sign_to_pdf(self):
        if not self.event_id.signature_template_id:
            return False
        packet = BytesIO()
        can = canvas.Canvas(packet)
        pdf = self.signature_request_id.template_id or self.event_id.signature_template_id
        # TODO: check necessity of sudo(). Does not work for group `Document Signatures` - Officer. Manager is mandatory
        itemsByPage = pdf.sudo().sign_item_ids.getByPage()
        attachment_data = self.event_id.signature_template_id.attachment_id.datas
        old_pdf = PdfFileReader(BytesIO(base64.b64decode(attachment_data)))
        for p in range(0, old_pdf.getNumPages()):
            page = old_pdf.getPage(p)
            width = float(page.mediaBox.getUpperRight_x())
            height = float(page.mediaBox.getUpperRight_y())

            items = itemsByPage[p + 1] if p + 1 in itemsByPage else []
            for item in items:
                value = self.sign_attachment_id and self.sign_attachment_id.datas
                if item.type_id.type == "signature" or item.type_id.type == "initial":
                    image_reader = ImageReader(BytesIO(base64.b64decode(value)))
                    _fix_image_transparency(image_reader._image)
                    can.drawImage(image_reader, width*item.posX, height*(1-item.posY-item.height), width*item.width, height*item.height, 'auto', True)

            can.showPage()


        can.save()
        item_pdf = PdfFileReader(packet, overwriteWarnings=False)
        new_pdf = PdfFileWriter()

        for p in range(0, old_pdf.getNumPages()):
            page = old_pdf.getPage(p)
            page.mergePage(item_pdf.getPage(p))
            new_pdf.addPage(page)

        output = BytesIO()
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
    signature_template_id = fields.Many2one('sign.template', string='Terms template')
    terms_to_sign = fields.Char(string='Event Terms')
    # rfid_templates = fields.Char(string='RFID Templates', help='Write it in the next way: 057 or 057,056,067')


class SignatureRequest(models.Model):
    _inherit = "sign.request"

    attendee_id = fields.Many2one('event.registration', string="Attendee")
