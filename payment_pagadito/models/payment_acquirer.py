# Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class AcquirerPaypal(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('pagadito', 'Pagadito')])
    pagadito_uid = fields.Char('Account ID', help='El identificador del Pagadito Comercio')
    pagadito_wsk = fields.Char('WSPG key (wsk)', help='La clave de acceso')
