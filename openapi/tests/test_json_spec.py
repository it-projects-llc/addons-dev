# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import HttpCase, PORT


class TestJsonSpec(HttpCase):
    at_install = True
    post_install = True

    def setUp(self):
        super(TestJsonSpec, self).setUp()
        self.opener.addheaders.append(("content-type", "application/json"))

    def test_json_base(self):

        resp = self.url_open("http://localhost:%d/api/v1/demo.json" % PORT,
                             timeout=30)
        self.assertEqual(resp.getcode(), 200, 'Cannot get json spec')
        # TODO add checking  actual content of the json
