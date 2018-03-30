# -*- coding: utf-8 -*-

import jinja2
import os
import requests
import random
import string
import odoo
from odoo import http
from odoo.http import request
from odoo.tools import config
from odoo.addons import web

path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
loader = jinja2.FileSystemLoader(path)
env = jinja2.Environment(loader=loader, autoescape=True)


class BackupDatabase(web.controllers.main.Database):

    def _render_template(self, **d):
        res = super(BackupDatabase, self)._render_template(**d)
        # Show button 'Restore via Odoo-backup.sh' on web/database/manager and web/database/selector pages
        place_for_backup_button = res.find(
            '<button type="button" data-toggle="modal" data-target=".o_database_restore"'
        )
        if place_for_backup_button == -1:
            place_for_backup_button = res.find(
                '<a role="button" data-toggle="modal" data-target=".o_database_restore" class="btn btn-link">'
            )
        if place_for_backup_button != -1:
            d['list_db'] = config['list_db']
            d['databases'] = []
            try:
                d['databases'] = http.db_list()
            except odoo.exceptions.AccessDenied:
                monodb = http.db_monodb()
                if monodb:
                    d['databases'] = [monodb]
            backup_button = env.get_template("backup_button.html").render(d)
            res = res[:place_for_backup_button] + backup_button + res[place_for_backup_button:]
        return res


class BackupController(http.Controller):

    @http.route('/web/database/backup_list', type='http', auth="none")
    def backup_list(self):
        config._parse_config()
        user_key = config.get('odoo_backup_user_key')
        if user_key is None:
            user_key = ''.join(random.choice(string.hexdigits) for _ in range(30))
            config.__setitem__('odoo_backup_user_key', user_key)
            config.save()
        headers = {
            'host': 'odoo-backup.sh',
            'Content-type': 'application/json',
            'Accept': 'text/plain'
        }
        res = requests.post(
            'http://odoo_backup_sh_service/web/backup/list', headers=headers, json={'params': {'user_key': user_key}}
        ).json()
        # TODO: check incompatible backups
        result = res['result']
        if result.get('success'):
            return env.get_template("backup_list.html").render(backup_list=result.get('backup_list'))
        else:
            redirect_url = request.httprequest.url_root + 'web/database/backup_list'
            url = 'http://%s/web/login?user_key=%s&redirect_url=%s' %(headers['host'], user_key, redirect_url)
            return "<html><head><script>window.location.href = '%s';</script></head></html>" % url
