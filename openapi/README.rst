d.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

===============================
 REST API / Open API (Swagger)
===============================

Set up REST API and export Open API (Swagger) specification file for
integration with whatever you need.

The module handles routes prefixed with ``/api/``. 

Authentication
==============

As a workaround for multi-db instances, system uses *Basic Authentication* with
``db_name:token`` credentials, where ``token`` is a new field in ``res.users``
model.

Customization
=============

The module allows to configure

* available models
* available operations per model (GRUD)

  * For reading:

    * field sets

.. TODO: add example of usage in API requests

  * For creation:

    * default values

.. TODO: add example of usage in API requests


Check `Usage instruction <doc/index.rst>`_ for details.

Credits
=======

Contributors
------------
* ` <https://it-projects.info/team/yelizariev>`__

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support you are kindly requested to purchase the module at `odoo apps store <https://apps.odoo.com/apps/modules/10.0/openapi/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/misc-addons/10.0

HTML Description: https://apps.odoo.com/apps/modules/10.0/openapi/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Notifications on updates: `via Atom <https://github.com/it-projects-llc/misc-addons/commits/10.0/openapi.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/misc-addons/commits/10.0/openapi.atom>`_

Tested on Odoo 10.0 87b42ad9a887faacbbefcab9dd0703a5c51ce28b
