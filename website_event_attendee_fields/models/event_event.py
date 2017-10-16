# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Event(models.Model):
    _inherit = 'event.event'
    attendee_fields = fields.Many2many('event.event.attendee_field')


class AttendeeField(models.Model):

    _name = 'event.event.attendee_field'

    sequence = fields.Integer('Sequence')
    field_id = fields.Many2one('ir.model.fields', domain="[('model_id.model', 'in', ['res.partner', 'event.registration'])]")
    field_name = fields.Char(related='field_id.name', readonly=True)
    field_description = fields.Char(related='field_id.field_description', readonly=True)
    is_required = fields.Boolean('Required', default=True)
    form_type = fields.Selection([
        ('color', 'Color'),
        ('date', 'Date'),
        ('datetime', 'Date and Time'),
        ('datetime-local', 'Date and Time (local)'),
        ('email', 'Email'),
        ('month', 'Month'),
        ('number', 'Number'),
        ('password', 'Password'),
        ('search', 'Search'),
        ('tel', 'Phone'),
        ('text', 'Text'),
        ('time', 'Time'),
        ('url', 'URL'),
        ('week', 'Week'),
    ], string='Type at Form')

    width = fields.Selection([
        (str(v), str(v))
        for v in xrange(1, 13)  # 13 is not included
    ], string='Width', help="Field of a width in the form. One row may have width up to 12")

    @api.multi
    def name_get(self):
        return [
            (r.id, '#%s: %s (width=%s)' % (r.sequence, r.field_name, r.width, ))
            for r in self
        ]
