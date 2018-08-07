# -*- coding: utf-8 -*-
# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import datetime
import logging
import os
import tempfile

try:
    import boto3
    import botocore
    from pretty_bad_protocol import gnupg
except ImportError as err:
    logging.getLogger(__name__).debug(err)

import odoo
from odoo import api, fields, models, exceptions
from odoo.tools import config
from odoo.tools.translate import _
from odoo.exceptions import UserError
from ..controllers.main import BackupController


class Dashboard(models.AbstractModel):
    _name = 'odoo_backup_sh.dashboard'
    _description = 'Backup Dashboard'

    @api.model
    def action_dashboard_redirect(self):
        return self.env.ref('odoo_backup_sh.backup_dashboard').read()[0]

    @api.model
    def update_info(self, redirect):
        res = BackupController().update_info(redirect)
        if 'backup_list' in res:
            res['dbs'] = [db for db in odoo.service.db.list_dbs() if db != 'session_store']
            backup_model = self.env['odoo_backup_sh.backup']
            backup_model.search([]).unlink()
            for bck in res['backup_list']:
                bck_vals = bck.split('|')
                backup_model.create({
                    'database': bck_vals[0],
                    'date_upload': datetime.datetime.strptime(bck_vals[1], '%Y-%m-%d_%H-%M-%S')
                })
        return res

    @api.model
    def make_backup(self, name):
        dump_stream = odoo.service.db.dump_db(name, None, 'zip')
        filename = name + '.zip'
        if self.env['ir.config_parameter'].get_param('odoo_backup_sh.encrypt_backups', 'False').lower() == 'true':
            passphrase = config.get('odoo_backup_encryption_password')
            if not passphrase:
                raise UserError(_('Encryption password is not found. Please check your module settings.'))
            filename += '.enc'
            # GnuPG ignores the --output parameter with an existing file object as value
            backup_encrpyted = tempfile.NamedTemporaryFile()
            backup_encrpyted_name = backup_encrpyted.name
            os.unlink(backup_encrpyted_name)
            gnupg.GPG().encrypt(
                dump_stream, symmetric=True, passphrase=passphrase, encrypt=False, output=backup_encrpyted_name)
            dump_stream = open(backup_encrpyted_name, 'rb')
        credentials = BackupController().get_cloud_params()
        s3_client = boto3.client('s3', aws_access_key_id=credentials['amazon_access_key'],
                                 aws_secret_access_key=credentials['amazon_secret_access_key'])
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        filename = "%s|%s" % (filename, ts)
        s3_path_key = '%s/%s' % (credentials['oauth_uid'], filename)
        try:
            s3_client.put_object(Body=dump_stream, Bucket=credentials['amazon_bucket_name'], Key=s3_path_key)
        except botocore.exceptions.ClientError as e:
            raise exceptions.ValidationError(_("Amazon error: ") + e.response['Error']['Message'])
        return None


class Backup(models.Model):
    _name = 'odoo_backup_sh.backup'
    _description = 'Information about backups'

    database = fields.Char(string='Database Name')
    date_upload = fields.Datetime(string='Upload Date')
