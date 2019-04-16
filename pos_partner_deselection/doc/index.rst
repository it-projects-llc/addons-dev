===================
Partner deselection
===================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

* Go to ``Point of Sale >> Configuration >> Point of Sale``

  * Select a Point of Sale (POS)
  * Click on ``[Edit]`` and then select  ``[Settings]``
  * Go to the Features section
  * Specify a **Customer Deselection Interval** in seconds
  * Click ``[Save]``

Usage
=====

* Open a Point of Sale (POS)
* Click ``Customers``
* Select a customer
* Click ``Set Customer``
* Wait for an amount time which you set up in Deselection Interval field.
* **RESULT:** Customer is Deselected after some amount of time
