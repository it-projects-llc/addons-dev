# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models
from google.oauth2 import service_account
from google.cloud import storage
import json

class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    google_cloud_storage_credentials = fields.Char(
        string="Google Application Credentials (for Google Cloud Storage)",
        config_parameter="google_cloud_storage.credentials"
    )
    google_cloud_storage_bucket = fields.Char(
        string="Bucket (for Google Cloud Storage)",
        config_parameter="google_cloud_storage.bucket"
    )


    def get_google_cloud_storage_client(self):
        icp = self.env["ir.config_parameter"].sudo()
        credentials = icp.get_param("google_cloud_storage.credentials")

        if not credentials:
            raise Exception("No Google Cloud Storage credendtials given")

        return storage.Client(
            None,
            credentials=service_account.Credentials.from_service_account_info(
                json.loads(credentials)
            )
        )

    def get_google_cloud_storage_bucket(self):
        client = self.get_google_cloud_storage_client()

        icp = self.env["ir.config_parameter"].sudo()
        bucket = icp.get_param("google_cloud_storage.bucket")

        if not bucket:
            raise Exception("No Google Cloud Storage bucket given")

        return client.get_bucket(bucket)


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icp = self.env["ir.config_parameter"].sudo()

        res.update(
            google_cloud_storage_credentials=icp.get_param(
                "google_cloud_storage.credentials", ""
            ),
            google_cloud_storage_bucket=icp.get_param(
                "google_cloud_storage.bucket", ""
            ),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param(
            "google_cloud_storage.credentials",
            self.google_cloud_storage_credentials or "{}",
        )
        icp.set_param(
            "google_cloud_storage.bucket",
            self.google_cloud_storage_bucket or "",
        )
