from odoo import http
from odoo.http import request
import json


class PosESignExtension(http.Controller):

    @http.route('/pos_longpolling/submit_sign', type="json", auth="user")
    def submit_kiosk_sign(self, vals):
        config_id = request.env["pos.config"].browse(vals.get('config_id', 0))
        res = self.update_partner_sign(vals)

        if res and config_id:
            channel_name = "pos.sign_request"
            config_id._send_to_channel_by_id(config_id._cr.dbname, config_id.id, channel_name, json.dumps(res))

        return True
