# -*- coding: utf-8 -*-
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api
from odoo import fields
from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    phonetic_name = fields.Char('Customer Phonetic Name')


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def load_history(self, limit=0):
        """
        :param int limit: max number of records to return
        :return: dictionary with keys:
             * partner_id: partner identification
             * history: list of dictionaries
                 * date
                 * origin
                 * state
                 * finishing_date
        """
        fields = [
            # 'pos_reference',
            'origin',
            'date',
            'state',
            'finishing_date',
        ]
        data = dict((id, {'history': [],
                          'partner_id': id,
                          }) for id in self.ids)

        for partner_id in self.ids:
            records = self.env['mrp.production'].search_read(
                domain=[('partner_id', 'in', self.ids)],
                fields=fields,
                limit=limit,
            )
            data[partner_id]['history'] = records
        return data
