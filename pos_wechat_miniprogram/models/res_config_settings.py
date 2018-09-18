# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sms_verification_template = fields.Many2one('qcloud.sms.template', string='SMS Verification Template',
                                                help='Used to verify a user with a text SMS message')

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('qcloud.sms_template_id', self.sms_verification_template.id)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        sms_template_id = get_param('qcloud.sms_template_id', default=False),
        if sms_template_id:
            res.update(
                sms_verification_template=sms_template_id,
            )
        return res
