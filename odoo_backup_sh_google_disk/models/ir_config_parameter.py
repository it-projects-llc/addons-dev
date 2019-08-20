# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging
from odoo import models, api


_logger = logging.getLogger(__name__)

try:
    from google.oauth2 import service_account
except ImportError as err:
    _logger.debug(err)

try:
    from googleapiclient.discovery import build
    from googleapiclient.discovery_cache.base import Cache
except ImportError as err:
    _logger.debug(err)

# all scopes you can find: here https://developers.google.com/identity/protocols/googlescopes
SCOPES = ['https://www.googleapis.com/auth/drive']


# https://stackoverflow.com/questions/15783783/python-import-error-no-module-named-appengine-ext
class MemoryCache(Cache):
    _CACHE = {}

    def get(self, url):
        return MemoryCache._CACHE.get(url)

    def set(self, url, content):
        MemoryCache._CACHE[url] = content


class Param(models.Model):

    _inherit = 'ir.config_parameter'

    @api.model
    def get_google_drive_service(self):
        service_account_file = self.get_param('odoo_backup_sh_google_disk.service_account_file')
        if not service_account_file:
            return
        # create a credentials
        credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
        # create a service using REST API Google Drive v3 and credentials
        service = build('drive', 'v3', credentials=credentials, cache=MemoryCache())
        return service
