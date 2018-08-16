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


SMS Tracking
------------
ALL SMS messages can be found at ``[[ Settings ]] >> Tencent Cloud SMS >> Messages``. If you don't have that menu, you need to `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__

SMS Templates
-------------
* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Open menu ``[[ Settings ]] >> Tencent Cloud SMS >> Templates``
* Click on ``[Create]``
* Specify ``Name`` and ``SMS Type``
* If necessary, specify other fields
* Click on ``[Save]``
