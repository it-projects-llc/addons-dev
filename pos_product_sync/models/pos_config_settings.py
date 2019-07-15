# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0.html).
from odoo import models, api, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_sync_field_ids = fields.Many2many('ir.model.fields', string='Synchronized Fields',
                                              domain=[('model', '=', 'product.product')])

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        for record in self:
            config_parameters.sudo().set_param("pos_product_sync.product_sync_field_ids",
                                               ', '.join(str(x) for x in record.product_sync_field_ids.ids))

    @api.multi
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        product_sync_field_ids = config_parameters.sudo().get_param("pos_product_sync.product_sync_field_ids", default=False)
        res.update(
            product_sync_field_ids=product_sync_field_ids and [int(x) for x in product_sync_field_ids.split(',')],
        )
        return res
