# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import requests
import logging

from odoo.tests.common import HttpCase, PORT

from ..controllers import pinguin

_logger = logging.getLogger(__name__)

USER_DEMO = 'base.user_demo'


class TestAPI(HttpCase):
    at_install = True
    post_install = True

    def setUp(self):
        super(TestAPI, self).setUp()
        self.demo_user = self.env.ref(USER_DEMO)

    def request(self, method, namespace, model, id='', **kwargs):
        url = "http://localhost:%d/api/v1/%s/%s/%s" % (PORT, namespace, model, id)
        return requests.request(method, url, timeout=30, **kwargs)

    def request_from_demo_user(self, *args, **kwargs):
        kwargs['auth'] = requests.auth.HTTPBasicAuth(self.session.db, self.demo_user.token)
        return self.request(*args, **kwargs)

    def test_read_many_all(self):
        namespace_name = 'demo'
        model_name = 'res.partner'
        resp = self.request_from_demo_user('GET', namespace_name, model_name)
        self.assertEqual(resp.status_code, 200)
        # TODO check content

    # def test_read_many_domain(self):
    #     resp = self.request_from_demo_user('GET', 'demo', 'res.partner', params = {'domain': '[("phone", "!=", False)]'})
    #     self.assertEqual(resp.status_code, 200)
    #     # TODO check content

    def test_read_one(self):
        namespace_name = 'demo'
        model_name = 'res.partner'
        id = self.env[model_name].search([], limit=1).id
        resp = self.request_from_demo_user('GET', namespace_name, model_name, id)
        self.assertEqual(resp.status_code, 200)
        # TODO check content

    def test_create_one(self):
        namespace_name = 'demo'
        model_name = 'res.partner'
        data_for_create = {
            'name': 'created_from_test',
            'type': 'other'
        }
        resp = self.request_from_demo_user('POST', namespace_name, model_name, data=data_for_create)
        self.assertEqual(resp.status_code, 201)
        # TODO: check creating in db
        # created_user = self.env[model_name].browse(resp.json()['id'])
        # self.assertEqual(created_user.name, data_for_create['name'])

    def test_update_one(self):
        namespace_name = 'demo'
        model_name = 'res.partner'
        data_for_update = {
            'name': 'for update in test',
        }
        partner = self.env[model_name].search([], limit=1)
        resp = self.request_from_demo_user('PUT', namespace_name, model_name, partner.id, data=data_for_update)
        self.assertEqual(resp.status_code, 204)
        # TODO: check content is changed
        # self.assertEqual(partner.name, data_for_update['name'])

    def test_unlink_one(self):
        namespace_name = 'demo'
        model_name = 'res.partner'
        partner = self.env[model_name].create({'name': 'record for deleting from test'})
        resp = self.request_from_demo_user('DELETE', namespace_name, model_name, partner.id)
        self.assertEqual(resp.status_code, 204)
        # TODO: check deleting from db
        # self.assertFalse(self.env[model_name].browse(partner.id).exists())

    def test_unauthorized_user(self):
        namespace_name = 'demo'
        model_name = 'res.partner'
        resp = self.request('GET', namespace_name, model_name)
        self.assertEqual(resp.status_code, 404)

    def test_invalid_dbname(self):
        namespace_name = 'demo'
        model_name = 'res.partner'
        db_name = 'invalid_db_name'
        resp = self.request('GET', namespace_name, model_name, auth=requests.auth.HTTPBasicAuth(db_name, self.demo_user.token))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()['error'], pinguin.CODE__db_not_found[1])

    def test_invalid_user_token(self):
        namespace_name = 'demo'
        model_name = 'res.partner'
        invalid_token = 'invalid_user_token'
        resp = self.request('GET', namespace_name, model_name, auth=requests.auth.HTTPBasicAuth(self.session.db, invalid_token))
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()['error'], pinguin.CODE__no_user_auth[1])

    # def test_user_not_allowed_for_namespace(self):
    #     namespace_name = 'demo'
    #     model_name = 'res.partner'
    #     namespace = self.env['openapi.namespace'].search([('name', '=', namespace_name)])
    #     namespace.write({
    #         'user_ids': [(3, self.demo_user.id, 0)]
    #     })
    #     resp = self.request_from_demo_user('GET', namespace_name, model_name)
    #     self.assertEqual(resp.status_code, 401)
    #     self.assertEqual(resp.json()['error'], pinguin.CODE__user_no_perm[1])
