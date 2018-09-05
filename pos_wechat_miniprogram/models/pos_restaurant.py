# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, models, fields
import werkzeug.urls


class RestaurantTable(models.Model):
    _inherit = 'restaurant.table'

    wechat_miniprogram_qr = fields.Binary(string='WeChat mini-program QR', attachment=True)

    @api.multi
    def get_miniprogram_qr_code(self, access_token=False):
        self.ensure_one()
        if not self.wechat_miniprogram_qr:
            param = {
                'floor_id': self.floor_id,
                'table_id': self.id
            }
            data = {
                "path": '%s?%s' % ('pages/index/index', werkzeug.urls.url_encode(param)),
                "width": 430
            }
            res = self.env['ir.config_parameter'].sudo().get_qr_code(data, access_token)
            self.wechat_miniprogram_qr = res
            return res

        return self.wechat_miniprogram_qr
