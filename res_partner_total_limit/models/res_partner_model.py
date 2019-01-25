# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _default_mail_template(self):
        try:
            return self.env.ref('res_partner_total_limit.partner_total_limit_email_template').id
        except ValueError:
            return False

    limit = fields.Float(string="Limit", translate=True)
    total = fields.Float(string="Total", readonly=True, translate=True)

    send_email_to_seller = fields.Boolean(string="Send notification to Email", translate=True, default=False)
    seller_email_template_id = fields.Many2one("mail.template", string="Email Template",
                                               domain="[('model_id.model','=','res.partner')]", translate=True,
                                               default=_default_mail_template)

    @api.multi
    def send_email_to_marketplace_seller(self):
        self.ensure_one()
        if self.send_email_to_seller:
            template_id = self.seller_email_template_id or False
            if not template_id:
                raise UserError(_('Please specify email template to send the notification. Model: res.partner'))
            template_id.send_mail(self.id, True)

            _logger.info("Sent an email about reaching the limit for the marketplace seller: %s" % (self.name))
