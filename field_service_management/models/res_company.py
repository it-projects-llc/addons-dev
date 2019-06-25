# See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    automatically_assign_jobs = fields.Boolean(
        string='Assign job automatically',
        help='Enable this option to automatically \
            assign jobs to the Serviceman based \
            on the service, area and city')
    automatic_fetch_address = fields.Boolean(
        string='Automatically Fetch Address',
        help='If checked the address will be \
            automatically fetched from the google \
            maps based on the latitude longitude \
            in the Job')
    default_password = fields.Char('Default Password', default='fsm')
