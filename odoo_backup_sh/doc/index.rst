================
 Odoo-backup.sh
================

Installation
============

* Install `a Python wrapper for GnuPG <https://pypi.org/project/pretty-bad-protocol>`__ ::

    pip install pretty-bad-protocol

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

* To enable the ability to restore databases from your remote backups in a new odoo instance:

  * Start Odoo with ``--load=web,odoo_backup_sh`` or set the ``server_wide_modules`` option in the Odoo configuration file:

::

  [options]
  # (...)
  server_wide_modules = web,odoo_backup_sh
  # (...)


.. todo:: Add the section when interfaces are ready.
{Instruction how to configure the module before start to use it}

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Open menu ``[[ {Menu} ]] >> {Submenu} >> {Subsubmenu}``
* Click ``[{Button Name}]``

Usage
=====

.. todo:: Add the section when interfaces are ready.
{Instruction for daily usage. It should describe how to check that module works. What shall user do and what would user get.} 

* Open menu ``{Menu} >> {Submenu} >> {Subsubmenu}``
* Click ``[{Button Name}]``
* RESULT: {what user gets, how the modules changes default behaviour}
