# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
import logging

from odoo import models, fields, api


_logger = logging.getLogger(__name__)


class Generator(models.TransientModel):
    _name = 'account.analytic.quant.generator'

    quant_amount = fields.Monetary(
        'Quant size'
    )
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)

    def apply(self):
        self.ensure_one()
        _logger.debug('Start quant generation')
        # TODO
