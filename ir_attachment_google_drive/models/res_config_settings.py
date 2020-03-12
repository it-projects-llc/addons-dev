# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    google_drive_attachment_condition = fields.Char(
        string="Google Drive Condition",
        help="""Specify valid odoo search domain here,
        e.g. [('res_model', 'in', ['product.image'])] -- store data of product.image only.
        Empty condition means all models""",
        config_parameter="google_drive.attachment_condition",
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icp = self.env["ir.config_parameter"].sudo()

        res.update(
            google_drive_attachment_condition=icp.get_param(
                "google_drive.attachment_condition", ""
            ),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param(
            "google_drive.attachment_condition",
            self.google_drive_attachment_condition or "",
        )
