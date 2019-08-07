# Copyright 2017 IT-Projects LLC (<https://it-projects.info>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models, api
from odoo.exceptions import Warning as UserError

from ..xmlrpc import rpc_execute_kw, rpc_auth

PURCHASE_ID = '__apps_odoo_com__.purchase_%s'
USER_ID = '__apps_odoo_com__.user_%s'
MODULE_ID = '__apps_odoo_com__.module_%s'


class UpdateData(models.TransientModel):
    _name = 'apps_odoo_com.update_data'
    _description = 'description of updatedata'

    @api.model
    def _update_data(self, domain):
        auth = rpc_auth(self.env)
        if not auth:
            return []
        search_read = rpc_execute_kw(
            self.env,
            'loempia.module.purchase',
            'search_read',
            rpc_kwargs={
                'domain': domain,
            })
        # {'purchase_order_ref': False, 'create_uid': [1, 'Administrator'], ... 'date_order': '2017-04-06 15:05:09', 'module_id': [13229, 'Delete "Sent by..." footer in email'], 'price': 9.0, 'quantity': 1.0}

        # local field -> remote field
        PURCHASE_FIELDS = {
            'id': 'id',
            'odoo_id': 'odoo_id',
            'purchase_order_ref': 'purchase_order_ref',
            # 'display_name': 'display_name',
            'user_id/id': 'user_id',
            'product_id': 'product_id',
            'referrer_module_id/id': 'referrer_module_id',
            'last_update': '__last_update',
            'order_id': 'order_id',
            'price_unit': 'price_unit',
            'price': 'price',
            'order_name': 'order_name',
            'state': 'state',
            # 'module_maintainer_id': 'module_maintainer_id',
            'module_id/id': 'module_id',
            'date_order': 'date_order',
            'quantity': 'quantity',
        }

        purchase_fields = [local_field for local_field in PURCHASE_FIELDS]

        user_index = {}  # id -> data
        module_index = {}  # id -> data

        for r in search_read:
            # user
            self._process_many2one(user_index, r['user_id'], USER_ID)
            # module
            self._process_many2one(module_index, r['module_id'], MODULE_ID, 'display_name')
            self._process_many2one(module_index, r['referrer_module_id'], MODULE_ID, 'display_name')

            # update id to use it in ir.model.data
            r['odoo_id'] = r['id']
            r['id'] = PURCHASE_ID % r['id']
            # update user
            r['user_id'] = r['user_id'] and USER_ID % r['user_id'][0]
            # update module
            r['module_id'] = r['module_id'] and MODULE_ID % r['module_id'][0]
            r['referrer_module_id'] = r['referrer_module_id'] and MODULE_ID % r['referrer_module_id'][0]
            for local_field, remote_field in PURCHASE_FIELDS.items():
                if local_field == remote_field:
                    continue
                r[local_field] = r[remote_field]

        user_fields = ['id', 'odoo_id', 'name']
        self._load('apps_odoo_com.user', user_fields, (r for id, r in user_index.items()))

        module_fields = ['id', 'odoo_id', 'display_name']
        self._load('apps_odoo_com.module', module_fields, (r for id, r in module_index.items()))

        self._load('apps_odoo_com.purchase', purchase_fields, search_read)

        self._update_modules()

    def _update_modules(self):
        odoo_ids = self.env['apps_odoo_com.module']\
                       .search([('version', '=', False)])\
                       .mapped(lambda r: r.odoo_id)

        if not odoo_ids:
            return

        auth = rpc_auth(self.env)
        if not auth:
            return []
        search_read = rpc_execute_kw(
            self.env,
            'loempia.module',
            'search_read',
            rpc_kwargs={
                'domain': [('id', 'in', odoo_ids)],
                'fields': ['version', 'name'],
            })

        for r in search_read:
            # update id to use it in ir.model.data
            r['id'] = MODULE_ID % r['id']
            version = r['version']
            try:
                version = '.'.join(version.split('.')[:2])
            except:
                pass

            r['version'] = version

        module_fields = ['id', 'name', 'version']
        self._load('apps_odoo_com.module', module_fields, search_read)

    def _process_many2one(self, index, value, id_template, name_field='name'):
        if not value:
            return
        id_ = value[0]
        name = value[1]
        if id_ not in index:
            index[id_] = {
                'id': id_template % id_,
                'odoo_id': id_,
                name_field: name,
            }

    def _load(self, model, fields, list_of_dict):
        data = []
        for r in list_of_dict:
            data.append([r[f] for f in fields])

        result = self.env[model].sudo().load(fields, data)

        if any(msg['type'] == 'error' for msg in result['messages']):
            warning_msg = "\n".join(msg['message'] for msg in result['messages'])
            raise UserError(warning_msg)

    @api.multi
    def get_new_data(self):
        self.ensure_one()
        search_read = self.env['apps_odoo_com.purchase'].search([], limit=1, order='odoo_id DESC')
        if not search_read:
            return self.get_all_data()
        odoo_id = search_read[0].odoo_id
        self._update_data([('id', '>', odoo_id)])

    @api.multi
    def get_all_data(self):
        self.ensure_one()
        self._update_data([])
