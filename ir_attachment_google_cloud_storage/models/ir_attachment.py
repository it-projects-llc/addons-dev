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

    @api.model_create_multi
    def create(self, vals_list):
        try:
            bucket = self.env["res.config.settings"].get_google_cloud_storage_bucket()
        except Exception:
            _logger.exception(
                "Google Cloud Storage is not configured properly. Keeping attachments as usual"
            )
            return super(IrAttachment, self).create(vals_list)

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
                if values.get("res_model") not in ["ir.ui.view", "ir.ui.menu"] and self._storage() != 'db' and data:
                    bin_data = base64.b64decode(data) if data else b''
                    checksum = self._compute_checksum(bin_data)
                    values.update({
                        'file_size': len(bin_data),
                        'checksum': checksum,
                        'index_content': self._index(bin_data, mimetype),
                        'store_fname': self._file_write_google_cloud_storage(bucket, bin_data, checksum),
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
