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

* Open menu ``[[ Settings ]] >> Dashboard``
* In *REST API* section click ``[Add Integration]``

  * Specify **Name** for integration, e.g. ``test``
  * Set **Log responses** **Full**
  * Click ``[Save]``

* Click smart-button ``Accessable models``
* Click ``[Create]``

  * Set **Model**, for example *res.users*
  * Configure allowed operations

    * **[x] Create via API**

      * Set **Creation Context Presets**, for example

        * **Name**: ``brussels``
        * **Context**: ``{'default_tz':'Europe/Brussels', 'default_lang':'fr_BE'}``

    * **[x] Read via API**

      * Set **Read One Fields** -- fields to return on reading one record
      * Set **Read Many Fields** -- fields to return on reading multiple records

    * **[x] Update via API**
    * **[x] Delete via API**

Authentication
--------------

* Open menu ``[[ Settings ]] >> Users >> Users``
* Select a user that will be used for iteracting over API
* In ``REST API`` tab:

  * Set **Allowed Integration**
  * In ``REST API`` tab Click  ``[Generate Access Token]``
  * Copy **Basic Authentication code** to use in any system that support REST API (Open API)

Configuration review
--------------------

All settings are available under menu ``[[ Settings ]] >> REST API`` (Available in `Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__)

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
