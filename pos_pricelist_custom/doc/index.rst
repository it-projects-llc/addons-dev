======================
 POS Pricelist Custom
======================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

* Go to ``[[Point of Sale]] >> Configuration >> Point of Sale`` menu

  * Click ``[Edit]``
  * Activate ``Pricelist`` option
  * Specify ``Available Pricelists``
  * Specify ``Default Pricelist``
  * Open ``Default Pricelist``
  * Specify ``POS Discount Policy``
  * Click ``[Save]`` for ``Default Pricelist``
  * Activate ``Default Pricelist for Orderline`` option
  * Click ``[Save]``

Usage
=====

* Go to ``[[Point of Sale]]`` menu
* Open POS session

  * Add products to order
  * Specify ``Customer``
  * Select ``Orderline``
  * Click ``[Default Pricelist]``

* RESULT: The orderline has a new unit price. The original price of the orderline is displayed below.
