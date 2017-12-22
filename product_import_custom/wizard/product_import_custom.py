# -*- coding: utf-8 -*-

import csv
import logging
import base64
import StringIO
import requests
import re
import hashlib
import os.path
import time
import itertools
import urllib2
from PIL import Image
from __builtin__ import False
from psycopg2 import IntegrityError


from odoo import models, fields, api, tools


_logger = logging.getLogger(__name__)


name_attribute_id = 1  # WTF???
nameRegex = r'[^A-Za-z0-9\:\|\u2018\(\)`\u2018+\xdf\u2018\xfc&\xdf\xd6\xf6\'\xe4\xfc\xf6\xc3\xa4öäüÖÄÜß\-_,\./ ]+'
treshholdTime = time.time() - 3600 * 24 * 30


# Implemented as Wizard, but it uses only via cron -- no need to use it via UI
class ProductImportCustom(models.TransientModel):
    _name = 'product_import_custom.wizard'

    product_url = fields.Char(
        'Product URL',
        default=lambda self: self.env['ir.config_parameter'].get_param('product_import_custom.product_url', ''))
    product_variant_url = fields.Char(
        'Product Variant URL',
        default=lambda self: self.env['ir.config_parameter'].get_param('product_import_custom.product_variant_url'))
    username = fields.Char(
        'Username',
        help='Remote server authentication username',
        default=lambda self: self.env['ir.config_parameter'].get_param('product_import_custom.username', ''))
    password = fields.Char(
        'Password',
        help='Remote server authentication password',
        default=lambda self: self.env['ir.config_parameter'].get_param('product_import_custom.password', ''))
    quoting = fields.Selection([
        ('"', "\" - Double quote"),
        ('\'', "' - Single quote"),
        ], string="Quote char", default='"')
    separator = fields.Selection([
        (',', ", - comma"),
        (';', "; - semicolon"),
        ], string="Delimiter", default=',')

    def _import(self, csv_product_template, csv_products):
        """Import parsed data.

        :param csv_product_template: {'x_template_code': 301, 'name': 'Mein Testprodukttemplate', 'pos_categ_id': int(1), 'image': ''}
        :param list csv_products:
            [{'default_code': 'TEST_VARIANTE1', 'name_additional': 'TEST_VARIANTEE1', 'price_extra': 25}
             {'default_code': 'TEST_VARIANTE2', 'name_additional': 'TEST_VARIANTEE2', 'price_extra': 10},
             {'default_code': 'TEST_VARIANTE3', 'name_additional': 'TEST_VARIANTEE3', 'price_extra': 15.00},
            ]
        """

        _logger.debug("trying to import product.template, x_template_code = %s", csv_product_template['x_template_code'])
        product = self.env['product.template'].search([
            ('x_template_code', '=', csv_product_template['x_template_code'])
        ])
        _logger.debug("Searching: found ids: %s", product)
        if len(product) == 0:
            # create
            product = self.env['product.template'].create(csv_product_template)
            _logger.debug("CREATED product.template with id %d ", product.id)
            productAttributeLine = self.env['product.attribute.line'].create({
                'product_tmpl_id': product.id,
                'attribute_id': name_attribute_id,
                'value_ids': [9, 10]  # WTF???
            })
        else:
            product = product[0]
            productAttributeLine = self.env['product.attribute.line'].search([
                ('product_tmpl_id', '=', product.id),
                ('attribute_id', '=', name_attribute_id),
            ])

            _logger.debug("UPDATING product.template with id %d", product)
            product.write(csv_product_template)
        leftoverVariantsIds = product.product_variant_ids.ids

        attributeValueIds = []
        for csv_product in csv_products:
            _logger.debug("trying to import product.product with default_code = %s" % csv_product['default_code'])

            csv_product['product_tmpl_id'] = product.id
            attributeValueForName = self.env['product.attribute.value'].search([
                ('name', '=', csv_product['name_additional']),
                ('attribute_id', '=', name_attribute_id),
            ])
            if len(attributeValueForName) == 0:
                attributeValueForName = self.env['product.attribute.value'].create({
                    'name': csv_product['name_additional'],
                    'attribute_id': name_attribute_id,
                })
            else:
                attributeValueForName = attributeValueForName[0]

            attributeValueIds.append(attributeValueForName.id)
            # csv_product['attribute_line_ids'] = [2]
            csv_product['attribute_value_ids'] = [(6, 0, attributeValueForName.ids)]
            productAttributeLineData = {
                'product_tmpl_id': product.id,
                'attribute_id': name_attribute_id,
                'value_ids': [(6, 0, attributeValueIds)],
            }
            productAttributeLine.write(productAttributeLineData)

            productVariant = self.env['product.product'].search([
                ('default_code', '=', csv_product['default_code'])
            ])
            if len(productVariant) == 0:
                self.env['product.product'].create(csv_product)
            else:
                productVariant = productVariant[0]
                productVariant.write(csv_product)
                if productVariant.id in leftoverVariantsIds:
                    del leftoverVariantsIds[leftoverVariantsIds.index(productVariant.id)]

            productPrice = self.env['product.attribute.price'].search([
                ('product_tmpl_id', '=', csv_product['product_tmpl_id']),
                ('value_id', '=', attributeValueForName.id)
            ])
            if len(productPrice) == 0:
                productPrice = self.env['product.attribute.price'].create({
                    'product_tmpl_id': csv_product['product_tmpl_id'],
                    'value_id': attributeValueForName.id
                })
            else:
                productPrice = productPrice[0]
            productPrice.write({'price_extra': csv_product['price_extra']})

        if leftoverVariantsIds:
            _logger.debug('Deactivate leftoverVariants = %s', leftoverVariantsIds)
            self.env['product.product'].search([
                ('id', 'in', leftoverVariantsIds)
            ]).write({'active': False})

    def _urlopen(self, url):
        req = urllib2.Request(url)
        if self.username:
            b64str = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
            req.add_header("Authorization", "Basic %s" % b64str)
        return urllib2.urlopen(req)

    @api.model
    def cron_execute(self):
        self.create({}).execute()

    @api.multi
    def execute(self):
        """Load URLs and call _parse_and_import"""
        self.ensure_one()

        product_file = self._urlopen(self.product_url)
        product_variant_file = self._urlopen(self.product_variant_url)
        # we don't need use with-block or other way to close files, because
        # they are from urlopen which doesn't required to be closed
        self._parse_and_import(product_file, product_variant_file)

    @api.multi
    def _read_csv(self, csv_file):
        """ Returns a CSV-parsed iterator of all non-empty lines in the file
            :throws csv.Error: if an error is detected during CSV parsing
            :throws UnicodeDecodeError: if ``options.encoding`` is incorrect
        """
        # based on method from base_import module

        # TODO: guess encoding with chardet? Or https://github.com/aadsm/jschardet
        encoding = 'utf-8'  # can be made customizable
        if encoding != 'utf-8':
            # csv module expect utf-8, see http://docs.python.org/2/library/csv.html
            csv_data = csv_file.read()
            csv_data = csv_data.decode(encoding).encode('utf-8')
            csv_file = StringIO(csv_data)

        csv_iterator = csv.reader(
            csv_file,
            quotechar=str(self.quoting),
            delimiter=str(self.separator),
        )
        rows = (
            [item.decode('utf-8') for item in row]
            for row in csv_iterator
            if any(x for x in row if x.strip())
        )
        # skip headers
        return itertools.islice(rows, 1, None)

    def _parse_and_import(self, product_file, product_variant_file):
        """Parse file-like objects (real file or result of urlopen). Doesn't close files!"""
        _logger.info("Processing product templates...")

        product_templates = {}
        images_data_dir = os.path.join(tools.config['data_dir'], 'product_import_custom', 'images')
        if not os.path.isdir(images_data_dir):
            os.makedirs(images_data_dir)

        for row in self._read_csv(product_file):
            name = re.sub(nameRegex, '', row[2], 0, re.UNICODE)
            if name != row[2]:
                _logger.warning('Bad product name: \nGOT %s \nNEW %s', row[2], name)
            csv_product_template = {'list_price': 0, 'x_template_code': int(row[0]), 'name': name, 'pos_categ_id': int(1), 'products': []}
            if row[19] != '':
                image_url = row[19].split('@')[0]
                try:
                    path_to_file = os.path.join(images_data_dir, hashlib.sha224(image_url).hexdigest() + "." + image_url.split('.')[-1])
                    if (not os.path.isfile(path_to_file)) or os.path.getmtime(path_to_file) < treshholdTime:
                        _logger.debug("downloading image \n%s TO\n%s", image_url, path_to_file)
                        req = requests.get(image_url)
                        if req.status_code == 200:
                            image_response = req.content
                            f = open(path_to_file, 'w')
                            f.write(image_response)
                            f.close()
                            pilImg = Image.open(path_to_file).convert('RGB')
                            pilImg.load()
                            pilImg.thumbnail((400, 400), Image.ANTIALIAS)
                            pilImg.save(path_to_file)
                        else:
                            _logger.debug("Image exists:\n%s -- Source\n%s -- File", image_url, path_to_file)

                    if os.path.isfile(path_to_file):
                        base64_image = base64.b64encode(open(path_to_file).read(100000))
                        csv_product_template['image'] = base64_image

                except Exception as e:
                    _logger.warning("Error on downloading image: %s", e.message)
            product_templates[row[0]] = csv_product_template

        _logger.info("Processing product variants...")
        for row in self._read_csv(product_variant_file):

            if row[6] not in product_templates:
                _logger.warning("key %s not found" % row[6])
                continue

            if row[2] != '':
                product_templates[row[6]]['pos_categ_id'] = int(row[2])
            name_additional = re.sub(nameRegex, '', row[3], 0, re.UNICODE)
            csv_product = {'name_additional': name_additional.strip(),
                           'taxes_id': [[6, 0, [int(row[5])]]],
                           'price_extra': row[4],
                           'default_code': row[1]
                           }
            found = False
            for product in product_templates[row[6]]['products']:
                # _logger.debug(product)
                if product['name_additional'] == csv_product['name_additional']:
                    found = True

            if not found:
                product_templates[row[6]]['products'].append(csv_product)
            product_templates[row[6]]['taxes_id'] = csv_product['taxes_id']

        for key, product in product_templates.iteritems():
            variants = product.pop('products')
            try:
                self._import(product, variants)
            except IntegrityError:
                # IntegrityError leads to blocking all futher updates, so raise and stop executing
                raise
            except Exception as e:
                _logger.warning('Error on importing', exc_info=True)
