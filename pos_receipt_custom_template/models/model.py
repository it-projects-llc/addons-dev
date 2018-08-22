# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    custom_invoice_receipt = fields.Boolean(string="Custom Invoice Receipt", defaut=False)
    custom_invoice_receipt_id = fields.Many2one("pos.custom_receipt", string="Custom Invoice Receipt",
                                                domain=lambda self: self._get_custom_xml_receipt_id_domain())
