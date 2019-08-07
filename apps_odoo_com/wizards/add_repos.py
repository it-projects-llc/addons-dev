# -*- coding: utf-8 -*-
# Copyright 2017 IT-Projects LLC (<https://it-projects.info>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import sys
import traceback
import logging

from openerp import models, fields, api

from ..xmlrpc import rpc_execute_kw, rpc_auth


_logger = logging.getLogger(__name__)


class AddRepos(models.TransientModel):
    _name = 'apps_odoo_com.add_repos'

    @api.model
    def _get_versions(self):
        auth = rpc_auth(self.env)
        if not auth:
            return []
        search_read = rpc_execute_kw(
            self.env,
            'loempia.series',
            'search_read',
            rpc_kwargs={
                'fields': ['name'],
            })
        res = [(r.get('id'), r.get('name'))
               for r in sorted(search_read,
                               key=lambda r: r.get('name')
                               )]
        return res

    version = fields.Selection(_get_versions, string='Version', required=True)

    repos = fields.Text('Repository List',
                        required=True,
                        help="One repo per line. ")

    @api.multi
    def apply(self):
        self.ensure_one()
        version_dict = dict(self._fields['version'].selection(self))
        version = version_dict[int(self.version)]
        for r in self.repos.split('\n'):
            _logger.info('Working with %s', r)
            if not r:
                continue
            if not r.endswith('.git'):
                r = r + '.git'
            r = '%s#%s' % (r, version)
            _logger.info('Final url: %s', r)
            try:
                repo_id = rpc_execute_kw(
                    self.env,
                    'loempia.repo',
                    'create',
                    rpc_args=[{
                        'url': r,
                        'series_id': self.version,
                    }])
                _logger.info('Repo created: %s', repo_id)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback)
                continue

            _logger.info('Validating...')
            try:
                rpc_execute_kw(
                    self.env,
                    'loempia.repo',
                    'validate',
                    rpc_args=[[repo_id]])
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback)
                continue
