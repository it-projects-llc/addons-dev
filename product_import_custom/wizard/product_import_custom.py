# -*- coding: utf-8 -*-

import logging
import smtplib
import urllib2, base64
from io import BytesIO
import StringIO
import requests
import csv
import xmlrpclib
import re
import pprint
import sys
import hashlib
import os.path
import time
import codecs
from PIL import Image
from __builtin__ import False


from odoo import models, fields, api


_logger = logging.getLogger(__name__)


name_attribute_id = 1
nameRegex =  '[^A-Za-z0-9\:\|\u2018\(\)`\u2018+\xdf\u2018\xfc&\xdf\xd6\xf6\'\xe4\xfc\xf6\xc3\xa4öäüÖÄÜß\-_,\./ ]+'
treshholdTime = time.time() - 3600 * 24 * 30


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


# Implemented as Wizard, but it uses only via cron -- no needs to use it via UI
class ProductImportCustom(models.TransientModel):
    _name = 'product_import_custom.wizard'


    product_url = fields.Char(
        'Product URL',
        default=lambda self: self.env['ir.config_parameter'].get_param('product_import_custom.product', ''))
    product_variant_url = fields.Char(
        'Product Variant URL',
        default=lambda self: self.env['ir.config_parameter'].get_param('product_import_custom.product_variant'))

    def _import(self, csv_product_template, csv_products):
        """Import parsed data"""
    #csv_product_template = {'x_template_code': 301, 'name' : 'Mein Testprodukttemplate', 'pos_categ_id': int(1), 'image' : ''}
    #csv_products = [{'default_code' : 'TEST_VARIANTE1', 'name_additional' : 'TEST_VARIANTEE1', 'price_extra' : 25},
     #               {'default_code' : 'TEST_VARIANTE2', 'name_additional' : 'TEST_VARIANTEE2', 'price_extra' : 10},
     #               {'default_code' : 'TEST_VARIANTE3', 'name_additional' : 'TEST_VARIANTEE3', 'price_extra' : 15.00},
     #               ]

        _logger.debug("trying to import product.template, x_template_code = %s" % csv_product_template['x_template_code'])
        productIds = models.execute_kw(rpc_db, uid, rpc_password, 'product.template', 'search', [[('x_template_code', '=', csv_product_template['x_template_code'])]])
        _logger.debug("Searching: found ids:")
        pp.pprint(productIds)
        if len(productIds) == 0:
            # create
            productId = models.execute(rpc_db, uid, rpc_password, 'product.template', 'create', csv_product_template)
            _logger.debug("CREATED product.template with id %d " % (productId))
            productAttributeLineIds = [models.execute(rpc_db, uid, rpc_password, 'product.attribute.line', 'create', {'product_tmpl_id' : productId, 'attribute_id' : name_attribute_id, 'value_ids' : [9,10]})]
            productIds = [productId]
        else:
            productAttributeLineIds = models.execute(rpc_db, uid, rpc_password, 'product.attribute.line', 'search', [('product_tmpl_id', '=', productIds[0]), ('attribute_id', '=', name_attribute_id)])

        _logger.debug("UPDATING product.template with id %d" % productIds[0])
        models.execute(rpc_db, uid, rpc_password, 'product.template', 'write', productIds, csv_product_template)
        pData = models.execute(rpc_db, uid, rpc_password, 'product.template', 'read', productIds)
        leftoverVariants = pData[0]['product_variant_ids']
        #pp.pprint(pData)

        attributeValueIds = []
        for csv_product in csv_products:
            _logger.debug("trying to import product.product with default_code = %s" % csv_product['default_code'])

            csv_product['product_tmpl_id'] = productIds[0]
            attributeValueIdForName = models.execute(rpc_db, uid, rpc_password, 'product.attribute.value', 'search', [('name', '=', csv_product['name_additional']), ('attribute_id', '=', name_attribute_id)])
            if len(attributeValueIdForName) == 0:
                attributeValueIdForName = [models.execute(rpc_db, uid, rpc_password, 'product.attribute.value', 'create', {'name' : csv_product['name_additional'], 'attribute_id' : name_attribute_id})]

            attributeValueIds.append(attributeValueIdForName[0])
           # csv_product['attribute_line_ids'] = [2]
            csv_product['attribute_value_ids'] = [[6,0,attributeValueIdForName]]
            productAttributeLine = {'product_tmpl_id' : productIds[0], 'attribute_id' : name_attribute_id, 'value_ids' : [[6,0,attributeValueIds]]}
            #pp.pprint(productAttributeLine)
            productAttributeLine = models.execute(rpc_db, uid, rpc_password, 'product.attribute.line', 'write', productAttributeLineIds, productAttributeLine)

            #pp.pprint(csv_product)
            productVariantIds = models.execute_kw(rpc_db, uid, rpc_password, 'product.product', 'search', [[('default_code', '=', csv_product['default_code'])]])
            if len(productVariantIds) == 0:
                models.execute(rpc_db, uid, rpc_password, 'product.product', 'create', csv_product)
            else:
                models.execute(rpc_db, uid, rpc_password, 'product.product', 'write', productVariantIds, csv_product)
                if productVariantIds[0] in leftoverVariants:
                    del leftoverVariants[leftoverVariants.index(productVariantIds[0])]

            productPriceId = models.execute(rpc_db, uid, rpc_password, 'product.attribute.price', 'search', [('product_tmpl_id', '=', csv_product['product_tmpl_id']), ('value_id', '=', attributeValueIdForName[0])])
            if len(productPriceId) == 0:
                productPriceId = [models.execute(rpc_db, uid, rpc_password, 'product.attribute.price', 'create', {'product_tmpl_id' : csv_product['product_tmpl_id'], 'value_id' : attributeValueIdForName[0]})]
            models.execute(rpc_db, uid, rpc_password, 'product.attribute.price', 'write', productPriceId, {'price_extra' : csv_product['price_extra']})


        #try:
        pp.pprint(leftoverVariants)
        models.execute(rpc_db, uid, rpc_password, 'product.product', 'write', leftoverVariants, {'active' : False})
        #except:
        #    _logger.debug("cannot delete %s" % leftoverVariants)
        #pData = models.execute(rpc_db, uid, rpc_password, 'product.template', 'read', productIds)
        #ppData = models.execute(rpc_db, uid, rpc_password, 'product.product', 'read', pData[0]['product_variant_ids'])
        #pp.pprint(pData)
        #pp.pprint(ppData)


    def execute(self):
        """Load URLs and call _parse_and_import"""
        pp = pprint.PrettyPrinter(indent=4)


        # connection
        common = xmlrpclib.ServerProxy('{}/xmlrpc/common'.format(rpc_url))
        uid = common.authenticate(rpc_db, rpc_username, rpc_password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/object'.format(rpc_url))




        #get csv product_template data
        req = urllib2.Request(csv_artikel)
        b64str = base64.encodestring('%s:%s' % (csv_username, csv_password)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % b64str)
        result = urllib2.urlopen(req)

        artikel = result.read()
        f = open(product_csv, 'w')
        f.write(artikel)
        f.close()

        if len(artikel) > 0:
            _logger.debug("Got artikel data")

        req = urllib2.Request(csv_varianten)
        b64str = base64.encodestring('%s:%s' % (csv_username, csv_password)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % b64str)
        result = urllib2.urlopen(req)
        varianten = result.read()
        if len(varianten) > 0:
            _logger.debug("Got varianten data")
        f = open(product_variant_csv, 'w')
        f.write(varianten)
        f.close()

    def _parse_and_import(self, product_file, product_variant_file):
        """Parse file-like objects (real file or result of urlopen). Doesn't close files!"""

        with open(product_csv, 'r') as products:
            artikel = products.read()

            _logger.debug("processing templates...")
            f = BytesIO(artikel)
            product_reader = UnicodeReader(f, delimiter=',')
            i = 0
            product_templates = {}
            for row in product_reader:
                if i == 0:
                    i = i + 1
                    continue
                name = re.sub(nameRegex, '', row[2], 0, re.UNICODE)
                if name != row[2]:
                    pp.pprint(name)
                    pp.pprint(row[2])
                csv_product_template = {'list_price' : 0, 'x_template_code' : int(row[0]), 'name' : name, 'pos_categ_id': int(1), 'products' : []}
                if row[19] != '':
                    image_url = row[19].split('@')[0]
                    try:
                        path_to_file = "/tmp" + hashlib.sha224(image_url).hexdigest() + "." + image_url.split('.')[-1]
                        if (not os.path.isfile(path_to_file)) or os.path.getmtime(path_to_file) < treshholdTime:
                            _logger.debug("downloading image... %s" % image_url)
                            req = requests.get(image_url)
                        if req.status_code == 200:
                            image_response = req.content
                            f = open(path_to_file, 'w')
                            f.write(image_response)
                            f.close()
                            pilImg = Image.open( path_to_file ).convert('RGB')
                            pilImg.load()
                            pilImg.thumbnail((400, 400), Image.ANTIALIAS)
                            pilImg.save(path_to_file)
                            if os.path.isfile(path_to_file):
                                base64_image = base64.b64encode(open(path_to_file).read(100000))
                                csv_product_template['image'] = base64_image
                    except Exception as e:
                        pp.pprint(e.message)
                product_templates[row[0]] = csv_product_template
                i = i + 1


        # now product_templates is filled with data

        _logger.debug("processing products...")

        with open(product_variant_csv, 'r') as variants:
            varianten = variants.read()
            f = BytesIO(varianten)
            product_reader = UnicodeReader(f, delimiter=',')
            i = 0
            #print(product_templates)
            for row in product_reader:
                if i == 0:
                    i = i + 1
                    continue
                if not product_templates.has_key(row[6]):
                    _logger.debug("key %s not found" % row[6])
                    continue

                if row[2] != '':
                    product_templates[row[6]]['pos_categ_id'] = int(row[2])
                name_additional = re.sub(nameRegex, '', row[3], 0, re.UNICODE)
                csv_product = {'name_additional' : name_additional.strip(),
                                       'taxes_id': [[6,0,[int(row[5])]]], #row[5],
                                       'price_extra': row[4],
                                       'default_code' : row[1]
                                       }
                found = False
                for product in product_templates[row[6]]['products']:
                    #_logger.debug(product)
                    if product['name_additional'] == csv_product['name_additional']:
                        found = True

                if found == False:
                    product_templates[row[6]]['products'].append(csv_product)
                product_templates[row[6]]['taxes_id'] = csv_product['taxes_id']

        offset = 0
        start = True
        for key in product_templates:
            product = product_templates[key]
            if offset and product['x_template_code'] == offset:
                start = True
            if start == False:
                continue
            variants = product.pop('products')
            try:
                self._import_data(product, variants)
            except Exception as e:
                pp.pprint(e)
            time.sleep(1)
