# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models, http


class PosSession(models.Model):
    _inherit = 'pos.session'

    iface_cashdrawer = fields.Boolean(related='config_id.iface_cashdrawer')
    proxy_ip = fields.Char(related='config_id.proxy_ip')

    @http.route(['/pos_cashbox_pin/open_cashbox'], type='http', methods=['POST'], auth='public', website=True)
    @api.multi
    def open_backend_cashbox(self):
        print('cashbox opened')
