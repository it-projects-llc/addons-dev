# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import io
from odoo import fields, models, api
from odoo.tools import image
import codecs
from PIL import Image
Image.preinit()
Image._initialized = 2


class PosCustomReceipt(models.Model):
    _name = "pos.custom_receipt"

    name = fields.Char('Name')
    type = fields.Selection(string="Type", selection=[('receipt', 'Receipt'), ('ticket', 'Ticket')])
    image = fields.Binary("Image", attachment=True, help="This field holds the image used in receipt header")
    printable_image = fields.Binary("Printable Image",
                                    compute='_compute_printable_image', store=True,
                                    help="This field holds the appropriate image for the receipt header")
    qweb_template = fields.Text('Qweb')

    @api.depends('image')
    def _compute_printable_image(self):
        for rec in self:
            if not rec.image:
                return
            image_stream = io.BytesIO(codecs.decode(rec.image, 'base64'))
            image_open = Image.open(image_stream)
            image_size = (min(image_open.size[0], 225),
                          min(image_open.size[1], 225))

            rec.printable_image = image.image_resize_image(rec.image, image_size)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _get_custom_ticket_id_domain(self):
        return [('type', '=', 'ticket')]

    def _get_custom_xml_receipt_id_domain(self):
        return [('type', '=', 'receipt')]

    show_second_product_name_in_receipt = fields.Boolean(string="Display Second Product Name", default=False)
    show_discount_in_receipt = fields.Boolean(string="Display discount on the ticket", default=True,
                                              help="Check box if you want to display the discount "
                                                   "of the orderline on the ticket")

    custom_ticket = fields.Boolean(string="Custom Ticket", defaut=False)
    custom_ticket_id = fields.Many2one("pos.custom_receipt", string="Custom Template",
                                       domain=lambda self: self._get_custom_ticket_id_domain())

    custom_xml_receipt = fields.Boolean(string="Custom PosBox Receipt", defaut=False)
    custom_xml_receipt_id = fields.Many2one("pos.custom_receipt", string="Custom PosBox Receipt Template",
                                            domain=lambda self: self._get_custom_xml_receipt_id_domain())


class ProductTemplate(models.Model):
    _inherit = "product.template"

    second_product_name = fields.Char(string="Second Product Name")
