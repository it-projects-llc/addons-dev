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


class AttendeeField(models.Model):

    _inherit = 'event.event.attendee_field'

    field_type = fields.Selection(related='field_id.ttype', readonly=True)
