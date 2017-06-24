====================
 Real Multi Website
====================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

It's recommended to redirect backend requests (e.g. via nginx) to some specific host to avoid needless switching between companies for authenticated users. For example:

    shop1.example.com/web -> backend.example.com/web
    shop2.example.com/web -> backend.example.com/web

Otherwise opening backend page (i.e. /web) twice via two different hosts by the same user leads to sending updating company requests to database too often.

Configuration
=============

* `Enable technical features <https://odoo-development.readthedocs.io/en/latest/odoo/usage/technical-features.html>`__
* Open menu ``Website Admin >> Configuration >> Websites``
* Create or select a website record
* Update fields:

  * **Host Name**: host value without *www*
  * **Company**: which company is used for this *website*

Usage
=====

For all examples below:

* configure some WEBSITE1 for HOST1 and COMPANY1
* configure some WEBSITE2 for HOST2 and COMPANY2


Scenario for Website
--------------------

* open HOST1/
* add Text block "text1" to Home Page
* open HOST2/ -- you don't see "text1"
* add Text block "text2" to Home Page
* open HOST1/ -- you see "text1" and don't see "text2"

The same works if you create new page, new menu, update anything at website footer, etc.

Scenario for eCommerce
----------------------

* install ``website_shop`` (eCommerce) module
* open HOST1/shop, make order, open backend -- created order belongs to COMPANY1
* open HOST2/shop, make order, open backend -- created order belongs to COMPANY2
