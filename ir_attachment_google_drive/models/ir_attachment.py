# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

import base64
import json
import logging

import requests
from urllib3.fields import RequestField
from urllib3.filepost import choose_boundary, encode_multipart_formdata

from odoo import api, models
from odoo.tools import human_size
from odoo.tools.safe_eval import safe_eval

from odoo.addons.google_account.models.google_service import TIMEOUT

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

PREFIX = "google_drive://"


# https://stackoverflow.com/a/47682897
def encode_multipart_related(fields, boundary=None):
    if boundary is None:
        boundary = choose_boundary()

    body, _ = encode_multipart_formdata(fields, boundary)
    content_type = str("multipart/related; boundary=%s" % boundary)

    return body, content_type


def encode_media_related(metadata, media, media_content_type):
    rf1 = RequestField(
        name="placeholder",
        data=json.dumps(metadata),
        headers={"Content-Type": "application/json; charset=UTF-8"},
    )
    rf2 = RequestField(
        name="placeholder2", data=media, headers={"Content-Type": media_content_type},
    )
    return encode_multipart_related([rf1, rf2])


class IrAttachment(models.Model):

    _inherit = "ir.attachment"

    def _get_google_drive_auth_header(self):
        access_token = self.env.context.get("google_drive_access_token")
        if not access_token:
            access_token = self.env["google.drive.config"].get_access_token()
        return {"Authorization": "Bearer " + access_token}

    # это нагло скопировано с ir_attachment_url
    def _filter_protected_attachments(self):
        return self.filtered(
            lambda r: r.res_model not in ["ir.ui.view", "ir.ui.menu"]
            or not r.name.startswith("/web/content/")
            or not r.name.startswith("/web/static/")
        )

    @api.model_create_multi
    def create(self, vals_list):
        try:
            google_drive_access_token = self.env[
                "google.drive.config"
            ].get_access_token()
        except Exception:
            _logger.exception(
                "Google Drive is not configured properly. Keeping attachments as usual"
            )
            return super(IrAttachment, self).create(vals_list)

        self = self.with_context(
            google_drive_access_token=google_drive_access_token
        )

        # based on https://github.com/odoo/odoo/blob/fa852ba1c5707b71469c410063f338eef261ab2b/odoo/addons/base/models/ir_attachment.py#L506-L524
        record_tuple_set = set()
        for values in vals_list:
            # remove computed field depending of datas
            for field in ('file_size', 'checksum'):
                values.pop(field, False)
            values = self._check_contents(values)
            if 'datas' in values:
                # ===============
                # check, if attachment must be saved as google drive attachment
                # start
                data = values.pop('datas')
                mimetype = values.pop('mimetype')
                # TODO: not using google_drive.attachment_condition
                if values.get("res_model") not in ["ir.ui.view", "ir.ui.menu"] and self._storage() != 'db' and data:
                    bin_data = base64.b64decode(data) if data else b''
                    values.update({
                        'file_size': len(bin_data),
                        'checksum': self._compute_checksum(bin_data),
                        'index_content': self._index(bin_data, mimetype),
                        'store_fname': self._file_write_google_drive(data, values.get('name')),
                        'db_datas': False,
                    })
                else:
                    values.update(self._get_datas_related_values(data, mimetype))
                # end
                # ===============
            # 'check()' only uses res_model and res_id from values, and make an exists.
            # We can group the values by model, res_id to make only one query when
            # creating multiple attachments on a single record.
            record_tuple = (values.get('res_model'), values.get('res_id'))
            record_tuple_set.add(record_tuple)
        for record_tuple in record_tuple_set:
            (res_model, res_id) = record_tuple
            self.check('create', values={'res_model':res_model, 'res_id':res_id})
        return super(IrAttachment, self).create(vals_list)

    def _file_read(self, fname, bin_size=False):
        if not fname.startswith(PREFIX):
            return super(IrAttachment, self)._file_read(fname, bin_size)

        file_id = fname[len(PREFIX) :]
        _logger.debug("reading file with id {}".format(file_id))

        if bin_size:
            request_url = "https://www.googleapis.com/drive/v2/files/{}".format(file_id)
        else:
            request_url = "https://www.googleapis.com/drive/v2/files/{}?alt=media".format(
                file_id
            )

        r = requests.get(
            request_url, headers=self._get_google_drive_auth_header(), timeout=TIMEOUT
        )
        r.raise_for_status()

        if bin_size:
            return human_size(int(r.json()["fileSize"]))
        else:
            return base64.b64encode(r.content)

    def _file_write_google_drive(self, bin_value, original_filename):
        metadata = {}
        if original_filename:
            metadata["title"] = original_filename

        data, content_type = encode_media_related(
            metadata, bin_value, "application/octet-stream"
        )

        headers = self._get_google_drive_auth_header()
        headers["Content-Type"] = content_type

        r = requests.post(
            "https://www.googleapis.com/upload/drive/v2/files?uploadType=multipart",
            headers=headers,
            data=data,
        )
        r.raise_for_status()
        file_id = r.json()["id"]
        _logger.debug("uploaded file with id {}".format(file_id))
        return PREFIX + file_id

    def _file_delete(self, fname):
        if not fname.startswith(PREFIX):
            return super(IrAttachment, self)._file_delete(fname)

        file_id = fname[len(PREFIX) :]

        r = requests.delete(
            "https://www.googleapis.com/drive/v2/files/{}".format(file_id),
            headers=self._get_google_drive_auth_header(),
            timeout=TIMEOUT,
        )
        r.raise_for_status()
