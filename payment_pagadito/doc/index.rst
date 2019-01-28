===========================
 Pagadito Payment Acquirer
===========================

Preparation
===========

* You will need account at https://www.pagadito.com/

Sandbox
=======

You can play with a module via sandbox account created on this website: https://sandbox.pagadito.com.

If you get error "¡Lo sentimos! Pagadito Comercios aún no está disponible en su país o región" (Pagadito is not supported in your country), contact support team to add your IP to whilelist

Configuration
=============

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Open menu ``[[ Settings ]] >> Technical >> Parameters >> System Parameters``
* Check that parameter``web.base.url`` exists and has correct address for eCommerce website.
* Open menu ``[[ Invoicing ]] >> Configuration >> Payments >> Payment Acquirers``
* Select *Pagadito* record and set following parameters:

  * **Account ID** -- *El identificador del Pagadito Comercio*
  * **WSPG key (wsk)**  --  *La clave de acceso*


Usage
=====

eCommerce
---------
* install ``website_sale`` module
* add a product to the cart
* checkout the order and select *Pagadito* as payment method
* proceed the payment at pagadito website
* RESULT: payment is done and processed at odoo backend

Portal
------
TODO

* install ``website_payment`` module
