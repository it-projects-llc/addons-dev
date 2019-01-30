# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################


from odoo import models, fields, api, _

class SellerStatusReasonWizard(models.TransientModel):
    _name = 'seller.status.reason.wizard'
    _description = "Seller Status Reason Wizard"

    @api.model
    def _get_seller(self):
        return self._context.get('active_id', False)

    seller_id = fields.Many2one("res.partner", string="Seller", default=_get_seller, domain=[("seller", "=", True)])
    reason = fields.Text(string="Reason", required="1")

    @api.multi
    def do_denied(self):
        self.ensure_one()
        if self.seller_id:
            self.seller_id.deny()
            self.seller_id.status_msg = self.reason
            reason_msg = "Deny Reason : " + self.reason
            self.seller_id.message_post(body=reason_msg)
            # self.seller_id.message_post(reason_msg, subtype='mail.mt_comment', message_type='comment')
            
