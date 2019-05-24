# Copyright 2017 IT-Projects LLC (<https://it-projects.info>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging
import xmlrpc.client

from odoo.exceptions import Warning as UserError
from odoo import _

_logger = logging.getLogger(__name__)


def rpc_auth(env, username=None, password=None, url="http://apps.odoo.com", dbname="apps"):
    username = username or env['ir.config_parameter'].sudo().get_param("apps_odoo_com.login", '').strip()
    password = password or env['ir.config_parameter'].sudo().get_param("apps_odoo_com.password", '').strip()
    if not (username and password):
        return False
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    uid = common.authenticate(dbname, username, password, {})
    if not uid:
        # for security reason log password only in debug level
        _logger.debug('Authenticate failed: %s', (dbname, username, password))
        raise UserError(_('Authentication failed: %s'), (dbname, username,))

    return dbname, models, uid, password


def rpc_execute_kw(env, model, method, rpc_args=None, rpc_kwargs=None, auth=None):
    rpc_args = rpc_args or []
    rpc_kwargs = rpc_kwargs or {}
    auth = None or rpc_auth(env)
    dbname, models, uid, password = auth
    _logger.debug('auth: %s', auth)
    _logger.debug('RPC Execute: env["%s"].%s(*%s, **%s)', model, method, rpc_args, rpc_kwargs)
    res = models.execute_kw(dbname, uid, password,
                            model, method, rpc_args, rpc_kwargs)
    _logger.debug('RPC Result: %s', res)
    return res
