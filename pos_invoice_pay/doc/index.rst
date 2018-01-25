=====================================
 Pay Sale Orders & Invoices over POS
=====================================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

Pay Sale Orders
---------------

* Open ``[[Sales]] >> Sale Orders`` menu

  * Click on ``[Create]``
  * Select a customer
  * Add products
  * Click on ``[Save]``
  * Click on ``[Confirm Sale]``

* Go to ``[[Point of Sale]]`` menu
* Open POS session

  * Click on ``[Fetch Orders]``
  * Select Sale Order
  * Click on ``[Create Invoice]``
  * Select payment method on Payment screen
  * Click on ``[Validate]``

* Close POS session
* Open ``[[Invoicing]] >> Sales >> Customer Invoices`` menu
* See the corresponding paid invoice
	
Pay Invoices
------------

* Open ``[[Invoicing]] >> Sales >> Customer Invoices`` menu

  * Click on ``[Create]``
  * Select a customer
  * Add products
  * Click on ``[Save]``
  * Click on ``[Validate]``

* Go to ``[[Point of Sale]]`` menu
* Open POS session

  * Click on ``[Fetch Invoices]``
  * Select the invoice
  * Click on ``[Create Invoice]``
  * Select payment method on Payment screen
  * Click on ``[Validate]``

* Close POS session
* Open ``[[Invoicing]] >> Sales >> Customer Invoices`` menu
* See the corresponding paid invoice
