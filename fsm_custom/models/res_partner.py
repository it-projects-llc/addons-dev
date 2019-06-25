from odoo import api, fields, models, SUPERUSER_ID, _
import logging
logger = logging.getLogger(__name__)

class res_partner(models.Model):
    _inherit = 'res.partner'

    dob = fields.Date('Date of Birth')
    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice address'),
         ('delivery', 'Service address'),
         ('other', 'Other address')], string='Address Type',
        default='contact',
        help="Used to select automatically the right address according to the context in sales and purchases documents.")
