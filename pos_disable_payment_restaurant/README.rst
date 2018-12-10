.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

===============================================
 Disable options in POS (restaurant extension)
===============================================

Control access to POS Restaurant options

The mdoule adds new access rights on user form (``Extra Rights`` section):

* ``Point of Sale - Decrease Kitchen``
* ``Point of Sale - Remove Kitchen Orderline``

Notes:

* Deactivated ``Point of Sale - Remove Kitchen Orderline`` works only if the rights ``Point of Sale - Decrease Kitchen`` and ``Point of Sale - Decrease Kitchen`` are active
* The module depends on the OCA ``pos_access_right`` module. You must use `the latest update <https://github.com/OCA/pos/pull/304>`__ of this module

Credits
=======

Contributors
------------
* `Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>`__

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support you are kindly requested to purchase the module at `odoo apps store <https://apps.odoo.com/apps/modules/12.0/pos_disable_payment_restaurant/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/pos-addons/12.0

HTML Description: https://apps.odoo.com/apps/modules/12.0/pos_disable_payment_restaurant/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 12.0 b4c3268e38db273b1a750050e342aa4a1fd2b850
