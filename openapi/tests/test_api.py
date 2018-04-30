# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import requests
import logging

from odoo.tests.common import HttpCase, PORT


_logger = logging.getLogger(__name__)


class TestAPI(HttpCase):
    at_install = True
    post_install = True

    def setUp(self):
        super(TestAPI, self).setUp()
        self.opener.addheaders.append(("content-type", "application/json"))

    def request(self, method, model, params=None):
        url = "http://localhost:%d/api/v1/%s" % (PORT, model)
        headers = {
            "content-type": "application/json",
        }
        resp = requests.request(method, url, params=params, headers=headers, timeout=30)
        self.assertIn(resp.code, ['200'], 'Wrong response code')
        return resp.json()

    def test_read_many_all(self):
        self.request('GET', 'res.partner')
        # TODO check content

    def test_read_many_domain(self):
        self.request('GET', 'res.partner', {'domain': '[("phone", "!=", False)]'})
        # TODO check content

    # TODO rest methods
