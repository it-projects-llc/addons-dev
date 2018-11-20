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


_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    """Attendee"""
    _inherit = 'event.registration'

    @api.model
    def _get_random_token(self):
        """
            We set barcode templates to distinct event.registration barcode from attendee barcode (rfid)
         """
        return '052' + str(int(uuid.uuid4().bytes[:5].encode('hex'), 16))

    barcode = fields.Char(default=_get_random_token)
    rfid = fields.Char(related='partner_id.barcode')
    sign_attachment_id = fields.Many2one('ir.attachment', 'E-Sign')

    signed_terms = fields.Boolean('Terms are Signed', compute='_compute_signed_terms')
    requested_signature_ids = fields.One2many('signature.request', 'attendee_id', string='Requests')
    event_request_id = fields.Many2one('signature.request', string='Terms sign request')

    _sql_constraints = [
        ('barcode_rfid_uniq', 'unique(rfid, event_id)', "RFID Barcode should be unique per event")
    ]

    @api.multi
    @api.depends('sign_attachment_id')
    def _compute_signed_terms(self):
        for r in self:
            r.signed_terms = bool(r.sign_attachment_id)

    @api.model_cr_context
    def _init_column(self, column_name):
        """ to avoid generating a single default barcode when installing the module,
            we need to set the default row by row for this column """
        if column_name == "rfid":
            _logger.debug("Table '%s': setting default value of new column %s to unique values for each row",
                          self._table, column_name)
            self.env.cr.execute("SELECT id FROM %s WHERE rfid IS NULL" % self._table)
            registration_ids = self.env.cr.dictfetchall()
            query_list = [{'id': reg['id'], 'rfid': self._get_random_rfid_token()} for reg in registration_ids]
            query = 'UPDATE ' + self._table + ' SET rfid = %(rfid)s WHERE id = %(id)s;'
            self.env.cr._obj.executemany(query, query_list)
            self.env.cr.commit()

        else:
            super(EventRegistration, self)._init_column(column_name)

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
    def button_reg_close(self):
        if self.signed_terms:
            super(EventRegistration, self).button_reg_close()
        else:
            raise UserError(_("User must confirm the event terms at first"))

    @api.one
    def embed_sign_to_pdf(self):
        # TODO: it
        print 'Here is a commented code for embedding'
        # pdf = self.event_request_id.template_id
        # items = pdf.signature_item_ids
        # SignatureItemValue = self.env['signature.item.value']
        # old_pdf = PdfFileReader(StringIO.StringIO(base64.b64decode(self.template_id.attachment_id.datas)))
        # box = old_pdf.getPage(p).mediaBox
        # width = int(box.getUpperRight_x())
        # height = int(box.getUpperRight_y())
        # for item in items:
        #     if item.type_id.type == "signature" or item.type_id.type == "initial":
        #         img = base64.b64decode(self.sign_attachment_id[self.sign_attachment_id.find(',') + 1:])
        #         can.drawImage(ImageReader(StringIO.StringIO(img)), width * item.posX,
        #                       height * (1 - item.posY - item.height), width * item.width, height * item.height, 'auto',
        #                       True)



class EventEvent(models.Model):
    """Event"""
    _inherit = 'event.event'

    terms_to_sign = fields.Char(string='Event Terms')
    signature_template_id = fields.Many2one('signature.request.template', string='Terms template')

    @api.model
    def send_to_all_estes(self, channel_name, sub_channel, data):
        notifications = self.send_data_by_poll(channel_name, sub_channel, data)
        _logger.debug('EST notifications for %s: %s', self.ids, notifications)
        return

    @api.model
    def send_to_barcode_interface(self, channel_name, sub_channel, data):
        notifications = self.send_data_by_poll(channel_name, sub_channel, data)
        _logger.debug('Notifications from EST to BI for %s: %s', self.ids, notifications)
        return

    @api.model
    def send_data_by_poll(self, channel_name, sub_channel, data):
        channel = self._get_full_channel_name(channel_name, sub_channel)
        notifications = [[channel, data]]
        self.env['bus.bus'].sendmany(notifications)
        return notifications

    @api.multi
    def _get_full_channel_name(self, channel_name, sub_channel):
        self.ensure_one()
        return self._get_full_channel_name_by_id(self._cr.dbname, channel_name, sub_channel)

    @api.model
    def _get_full_channel_name_by_id(self, dbname, channel_name, sub_channel):
        return '["%s","%s","%s"]' % (dbname, channel_name, sub_channel)


class SignatureRequest(models.Model):
    _inherit = "signature.request"

    attendee_id = fields.Many2one('event.registration', string="Attendee")


class ResPartner(models.Model):
    """Partners"""
    _inherit = 'res.partner'

    @api.model
    def _get_random_rfid_token(self):
        """
            We set rfid templates to distinct event.registration barcode from attendee barcode (rfid)
         """
        return '053' + str(int(uuid.uuid4().bytes[:5].encode('hex'), 16))

    barcode = fields.Char(default=_get_random_rfid_token)
