# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

import base64
import json
import logging

from odoo import api, models
from odoo.tools import human_size

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

PREFIX = "google_cloud_storage://"


class IrAttachment(models.Model):

    _inherit = "ir.attachment"

    # это нагло скопировано с ir_attachment_url
    @api.multi
    def _filter_protected_attachments(self):
        return self.filtered(
            lambda r: r.res_model not in ["ir.ui.view", "ir.ui.menu"]
            or not r.name.startswith("/web/content/")
            or not r.name.startswith("/web/static/")
        )

    def _inverse_datas(self):
        our_records = self._filter_protected_attachments()

        if our_records:
            # make sure, you can use google drive
            # otherwise - use default behaviour
            try:
                bucket = self.env["res.config.settings"].get_google_cloud_storage_bucket()
            except Exception:
                _logger.exception(
                    "Google Cloud Storage is not configured properly. Keeping attachments as usual"
                )
                return super(IrAttachment, self)._inverse_datas()

        for attach in our_records:
            bin_value = base64.b64decode(attach.datas)
            checksum = self._compute_checksum(bin_value)
            fname = self._file_write_google_cloud_storage(bucket, bin_value, checksum)
            vals = {
                "file_size": len(bin_value),
                "checksum": checksum,
                "index_content": self._index(
                    bin_value, attach.datas_fname, attach.mimetype
                ),
                "store_fname": fname,
                "db_datas": False,
                "type": "binary",
                "datas_fname": attach.datas_fname,
            }
            super(IrAttachment, attach.sudo()).write(vals)

        return super(IrAttachment, self - our_records)._inverse_datas()

    def _file_read(self, fname, bin_size=False):
        if not fname.startswith(PREFIX):
            return super(IrAttachment, self)._file_read(fname, bin_size)

        bucket = self.env["res.config.settings"].get_google_cloud_storage_bucket()

        file_id = fname[len(PREFIX) :]
        _logger.debug("reading file with id {}".format(file_id))

        blob = bucket.get_blob(file_id)

        if bin_size:
            return human_size(blob.size)
        else:
            return base64.b64encode(blob.download_as_string())

    def _file_write_google_cloud_storage(self, bucket, bin_value, checksum):
        file_id = "odoo/{}".format(checksum)

        blob = bucket.blob(file_id)
        blob.upload_from_string(bin_value)

        _logger.debug("uploaded file with id {}".format(file_id))
        return PREFIX + file_id

    def _file_delete(self, fname):
        if not fname.startswith(PREFIX):
            return super(IrAttachment, self)._file_delete(fname)

        bucket = self.env["res.config.settings"].get_google_cloud_storage_bucket()

        file_id = fname[len(PREFIX) :]
        _logger.debug("deleting file with id {}".format(file_id))

        blob = bucket.get_blob(file_id)

        blob.delete()
