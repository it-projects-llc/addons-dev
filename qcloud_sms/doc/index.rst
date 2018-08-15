=======================
 Tencent Cloud SMS API
=======================

.. contents::
   :local:

Installation
============

* Install `qcloudsms_py library <https://github.com/qcloudsms/qcloudsms_py>`__::

    pip install qcloudsms_py

    # to update existing installation use
    pip install -U qcloudsms_py


Tencent Cloud SMS API
=====================

TODO

Configuration
=============

Credentials
-----------

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Open menu ``[[ Settings ]] >> Parameters >> System Parameters``
* Create following parameters

  * ``qcloudsms.app_id``
  * ``qcloudsms.app_key``


SMS tracking
------------
Tencent Cloud SMS messages can be found at ``[[ Invoicing ]] >> Configuration >> Tencent Cloud SMS``. If you don't have that menu, you need to configure ``Show Full Accounting Features`` for your user first:

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Open menu ``[[ Settings ]] >> Users & Companies >> Users``
* Open user you need
* Activate ``Show Full Accounting Features``
