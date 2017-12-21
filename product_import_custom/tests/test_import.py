# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestImport(TransactionCase):
    at_install = True
    post_install = True

    @classmethod
    def setUp(self):
        super(TestImport, self).setUp()
        self.wizard = self.env['product_import_custom.wizard'].create()

    def import_files(product_path, product_variant_path):
        with open(product_path, 'r') as product_file, \
             open(product_variant_path, 'r') as product_variant_file:

            self.wizard._parse_and_import(product_file, product_variant_file)

    def test_import_base(self):
        """Check that there is no errors during import"""
        self.import_files('product.csv', 'product_variant.csv')
