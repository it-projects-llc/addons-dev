# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import os
import tempfile
from datetime import datetime

try:
    from pretty_bad_protocol import gnupg
except ImportError as err:
    logging.getLogger(__name__).debug(err)

try:
    from dropbox.files import UploadSessionCursor
except ImportError as err:
    logging.getLogger(__name__).debug(err)

try:
    from dropbox.files import CommitInfo
except ImportError as err:
    logging.getLogger(__name__).debug(err)

import odoo
from odoo import api, models, fields
from odoo.addons.odoo_backup_sh.models.odoo_backup_sh import REMOTE_STORAGE_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


CHUNK_SIZE = 4 * 1024 * 1024

_logger = logging.getLogger(__name__)


class BackupConfig(models.Model):
    _inherit = "odoo_backup_sh.config"

    storage_service = fields.Selection(selection_add=[('dropbox', 'Dropbox')])

    @api.model
    def get_backup_list(self, cloud_params):
        backup_list = super(BackupConfig, self).get_backup_list(cloud_params) or dict()
        # get all backups from dropbox
        DropboxService = self.env['ir.config_parameter'].get_dropbox_service()
        folder_path = self.env['ir.config_parameter'].get_param("odoo_backup_sh_dropbox.dropbox_folder_path")
        response = DropboxService.files_list_folder(folder_path)
        drobpox_backup_list = [(r.name, 'dropbox') for r in response.entries]
        if 'backup_list' in backup_list:
            backup_list.update({
                'backup_list': backup_list['backup_list'] + drobpox_backup_list
            })
        else:
            backup_list['backup_list'] = drobpox_backup_list
        return backup_list

    @api.model
    def get_info_file_object(self, cloud_params, info_file_name, storage_service):
        if storage_service == 'dropbox':
            DropboxService = self.env['ir.config_parameter'].get_dropbox_service()
            folder_path = self.env['ir.config_parameter'].get_param("odoo_backup_sh_dropbox.dropbox_folder_path")
            full_path = "{folder_path}/{file_name}".format(
                folder_path=folder_path,
                file_name=info_file_name,
            )
            return DropboxService.files_download(full_path)
        else:
            return super(BackupConfig, self).get_info_file_object(cloud_params, info_file_name, storage_service)

    @api.model
    def create_info_file(self, info_file_object, storage_service):
        if storage_service == 'dropbox':
            info_file = tempfile.NamedTemporaryFile()
            info_file.write(info_file_object[1].content)
            info_file.seek(0)
            return info_file
        else:
            return super(BackupConfig, self).create_info_file(info_file_object, storage_service)

    @api.model
    def delete_remote_objects(self, cloud_params, remote_objects):
        folder_path = self.env['ir.config_parameter'].get_param("odoo_backup_sh_dropbox.dropbox_folder_path")
        DropboxService = self.env['ir.config_parameter'].get_dropbox_service()
        dropbox_remove_objects = []
        for file in remote_objects:
            if file[1] == 'dropbox':
                dropbox_remove_objects.append(file)
                full_path = "{folder_path}/{file_name}".format(
                    folder_path=folder_path,
                    file_name=file[0],
                )
                DropboxService.files_delete(full_path)

        return super(BackupConfig, self).delete_remote_objects(cloud_params, list(set(remote_objects) - set(dropbox_remove_objects)))

    @api.model
    def make_backup(self, name, service, init_by_cron_id=None):
        config_record = self.with_context({'active_test': False}).search([('database', '=', name),
                                                                          ('storage_service', '=', service)])
        if config_record.storage_service == 'dropbox':
            if init_by_cron_id and not self.env['ir.cron'].browse(init_by_cron_id).active:
                # The case when an auto backup was initiated by an inactive backup config.
                return None
            dump_stream = odoo.service.db.dump_db(name, None, 'zip')
            backup_name_suffix = '.zip'
            if config_record.encrypt_backups:
                backup_name_suffix += '.enc'
                # GnuPG ignores the --output parameter with an existing file object as value
                backup_encrpyted = tempfile.NamedTemporaryFile()
                backup_encrpyted_name = backup_encrpyted.name
                os.unlink(backup_encrpyted_name)
                gnupg.GPG().encrypt(dump_stream, symmetric=True, passphrase=config_record.encryption_password,
                                    encrypt=False, output=backup_encrpyted_name)
                dump_stream = open(backup_encrpyted_name, 'rb')
            backup_size = dump_stream.seek(0, 2) / 1024 / 1024
            dump_stream.seek(0)
            dt = datetime.utcnow()
            ts = dt.strftime(REMOTE_STORAGE_DATETIME_FORMAT)
            info_file = tempfile.TemporaryFile()
            info_file.write('[common]\n'.encode())
            info_file_content = {
                'database': name,
                'encrypted': True if '.enc' in backup_name_suffix else False,
                'upload_datetime': ts,
                'backup_size': backup_size,
                'storage_service': config_record.storage_service
            }
            for key, value in info_file_content.items():
                line = key + ' = ' + str(value) + '\n'
                info_file.write(line.encode())
            info_file_size = info_file.tell()
            info_file.seek(0)
            # Upload two backup objects to Dropbox
            DropboxService = self.env['ir.config_parameter'].get_dropbox_service()
            folder_path = self.env['ir.config_parameter'].get_param("odoo_backup_sh_dropbox.dropbox_folder_path")
            for obj, obj_name, file_size in \
                    [[dump_stream, "%s.%s%s" % (name, ts, backup_name_suffix), backup_size],
                     [info_file, "%s.%s%s" % (name, ts, '.info'), info_file_size]]:
                # The full path to upload the file to, including the file name
                full_path = "{folder_path}/{file_name}".format(
                    folder_path=folder_path,
                    file_name=obj_name,
                )
                # from here: https://www.dropboxforum.com/t5/API-Support-Feedback/python-upload-big-file-example/m-p/166627/highlight/true#M6013
                if file_size <= CHUNK_SIZE:
                    DropboxService.files_upload(obj.read(), full_path)
                else:
                    upload_session_start_result = DropboxService.files_upload_session_start(obj.read(CHUNK_SIZE))
                    cursor = UploadSessionCursor(session_id=upload_session_start_result.session_id, offset=obj.tell())
                    commit = CommitInfo(path=full_path)
                    while obj.tell() < file_size:
                        if ((file_size - obj.tell()) <= CHUNK_SIZE):
                            DropboxService.files_upload_session_finish(obj.read(CHUNK_SIZE), cursor, commit)
                        else:
                            DropboxService.files_upload_session_append(obj.read(CHUNK_SIZE), cursor.session_id, cursor.offset)
                            cursor.offset = obj.tell()

            # Create new record with backup info data
            info_file_content['upload_datetime'] = dt
            self.env['odoo_backup_sh.backup_info'].create(info_file_content)
            if init_by_cron_id:
                self.update_info()
            return None
        else:
            return super(BackupConfig, self).make_backup(name, service, init_by_cron_id)


class BackupInfo(models.Model):
    _inherit = 'odoo_backup_sh.backup_info'

    storage_service = fields.Selection(selection_add=[('dropbox', 'Dropbox')])


class BackupRemoteStorage(models.Model):
    _inherit = 'odoo_backup_sh.remote_storage'

    dropbox_used_remote_storage = fields.Integer(string='Dropbox Usage, MB', readonly=True)

    @api.multi
    def compute_total_used_remote_storage(self):
        self.compute_dropbox_used_remote_storage()
        super(BackupRemoteStorage, self).compute_total_used_remote_storage()

    @api.multi
    def compute_dropbox_used_remote_storage(self):
        amount = sum(self.env['odoo_backup_sh.backup_info'].search([('storage_service', '=', 'dropbox')]).mapped('backup_size'))
        today_record = self.search([('date', '=', datetime.strftime(datetime.now(), DEFAULT_SERVER_DATE_FORMAT))])
        if today_record:
            today_record.dropbox_used_remote_storage = amount
        else:
            self.create({
                'date': datetime.now(),
                'dropbox_used_remote_storage': amount
            })


class DeleteRemoteBackupWizard(models.TransientModel):
    _inherit = "odoo_backup_sh.delete_remote_backup_wizard"

    @api.multi
    def delete_remove_backup_button(self):
        record_ids = (self._context.get('active_model') == 'odoo_backup_sh.backup_info' and self._context.get('active_ids') or [])
        backup_info_records = self.env['odoo_backup_sh.backup_info'].search([('id', 'in', record_ids)])
        folder_path = self.env['ir.config_parameter'].get_param("odoo_backup_sh_dropbox.dropbox_folder_path")
        DropboxService = self.env['ir.config_parameter'].get_dropbox_service()
        backup_dropbox_info_records = backup_info_records.filtered(lambda r: r.storage_service == 'dropbox')

        for record in backup_dropbox_info_records:
            backup_files_suffixes = ['.zip', '.info']
            if record.encrypted:
                backup_files_suffixes[0] += '.enc'
            upload_datetime = datetime.strftime(record.upload_datetime, REMOTE_STORAGE_DATETIME_FORMAT)
            for suffix in backup_files_suffixes:
                obj_name = "%s.%s%s" % (record.database, upload_datetime, suffix)
                full_path = "{folder_path}/{file_name}".format(
                    folder_path=folder_path,
                    file_name=obj_name,
                )
                DropboxService.files_delete(full_path)
        backup_dropbox_info_records.unlink()
        super(DeleteRemoteBackupWizard, self).delete_remove_backup_button()
