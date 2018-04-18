===============================
 REST API / Open API (Swagger)
===============================

.. contents::
   :local:

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way
* Add ``openapi`` to ``--load`` parameters, e.g.::

    ./odoo --workers=2 --load openapi,web --config=/path/to/openerp-server.conf

Configuration
=============

Authentication
--------------

* Open menu ``[[ Settings ]] >> Users >> Users``
* Select a user that will be used for iteracting over API
* In ``REST API`` tab Click  ``[Generate Access Token]``
* Copy **Basic Authentication code** to use in any system that support REST API (Open API)


Activating and customization
----------------------------

via Model's Menu (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO

* Open menu with data you need to work over API
* Click button ``[Configure API]`` located near to ``Create
* Activate and configure operation you need to be available over API.  
* Click ``[Apply]``

via Database Structure Menu (only for developers)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Open menu ``[[ Settings ]] >> Technical >> Database Structure >> Models``
* Open model you need
* Switch to ``REST API`` tab
* Set some of operations and configuration for them:

  * **[x] Create via API**

    * Set Default Values

    * TODO: put this in the form view::

        Format for default values is
        * one-line per field, 
        * FIELD:VALUE
        * use slash for subfields, e.g. order_line/product_uom_qty

  * **[x] Read via API**

    * Set one or several *Fields Set* -- list of fields that can be used on
      requests for reading, for example ``short``, ``full``, ``for_magento``,
      etc.
    
    * TODO: put this in the form view::

          Format for Fields Set is 

          * one-line per field, 
          * use slash for subfields, e.g. order_line/product_uom_qty

  * **[x] Update via API**
  * **[x] Delete via API**

Usage
=====

TODO

* Open menu ``[[ Settings ]] >> Dashboard``
* In *REST API* section you can see Quantity of Models available via API
* Click button ``[Manage]`` to check or edit configuration
* Click link ``Download OpenAPI (Swagger)`` to get Specification file. Follow
  documentation of the tool / system you use on how to apply the Specification
  file there. Some examples are presented below.

Swagger Editor
--------------

Allows to review API

* Open http://editor.swagger.io/
* Click menu ``File >> Import File`` 
* RESULT: You can see specification for API
