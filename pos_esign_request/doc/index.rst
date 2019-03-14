====================
 POS E-Sign Request
====================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

To create a multi-session follow the steps:

* Open menu ``[[ Point of Sale ]] >> Configuration >> Point of Sale``
* Select a POS
* Click ``[Edit]``
* Activate **Ask To Sign** field
* Set **Terms & Conditions**
* If **E-Sign** is required for each purchase then activate **Mandatory Ask To Sign** field
* Click ``[Save]``

Usage
=====

You need two devices: one for POS, another one for taking signs

* Open a POS on a first device
* Open E-Sign Kiosk on the second device

    * Open menu ``[[ Point of Sale ]] >> Dashboard``
    * Click ``E-Sign`` on the same POS as opened on the first device

* On the first device click ``Customer`` button
* Select a Customer
* Click ``E-Sign`` button

* On the second device the form for signing appears
* Let the customer to draw a sign
* Click ``Submit Sign``

* On the first device for the customer in the **E-Sign** column ✔ sign appears
