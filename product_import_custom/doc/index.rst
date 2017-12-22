==============================================
 Sync products via remote csv (custom module)
==============================================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Open menu ``[[ Settings ]] >> Technical >> Parameters >> System Parameters``
* Update following parameters:

  * ``product_import_custom.product_url``
  * ``product_import_custom.product_variant_url``
  * ``product_import_custom.username`` (Remove this parameter if authentication is not needed)
  * ``product_import_custom.password``

* Open menu ``[[ Settings ]] >> Technical >> Automation >> Scheduled Actions``
* Open record named ``Sync products via remote csv``
* You can configure time (**Next Execution Date** field) and periodicity (**Interval number** and **Interval Unit**)

Usage
=====

Normally, cron will run task automatically at specified time. But if you need to try import immediately click ``[Run Manually]`` button at the cron task form.
