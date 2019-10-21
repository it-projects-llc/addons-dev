======================
 Sync Products in POS
======================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way
* Configure POS Longpolling (pos_longpolling) module as it's explained `here <https://apps.odoo.com/apps/modules/10.0/pos_longpolling/>`__

Configuration
=============

* Go to ``[Inventory] >> Configuration >> Settings``
* Check ``Attribute and Variants``
* In ``Point of Sale Product Synchronization Fields`` add fields that needed to be synchronized (i.e. name, price)

Usage
=====
* Open POS session
* Open backend in another browser window
  * Go to ``[Point of Sale] >> Catalog >> Product Variants``
  * Choose product
  * Change fields (i.e. name, price)

RESULT: In opened POS UI the product data is updated instantly without any extra action


