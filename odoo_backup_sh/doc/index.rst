================
 Odoo-backup.sh
================

Installation
============

* Install `a Python wrapper for GnuPG <https://pypi.org/project/pretty-bad-protocol>`__ ::

    pip install pretty-bad-protocol

* Install `Amazon Web Services (AWS) SDK for Python <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>`__ ::

    pip install boto3

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

In order for desired databases to appear in a backup dashboard, you have to create settings for it.
Open the menu ``[[ Backups ]] >> Dashboard``. Click on the ``[Add Database]`` button in the dashboard header.
Fill required fields:

- Database: select one of your databases
- Auto Backup Execute Every:  type a value and select a unit of measure.
  Example: You want the module to make new backup every 2 hours.
  If you want to create backups manually only, leave this field blank.
- Next Execution Date: It shows next planned auto backup date. You can correct this.
  Example: You want the module to make new backup every day at night time.
- Auto Rotation: If you have set up the auto backup, you can specify how many backups to preserve for certain time
  frames.
  Example: The module makes auto backup your database every 2 hours. You want to preserve 2 daily backups and 1 weekly.
  Just put this numbers in appropriate fields. Then you will have one last backup of last week and two last backups of
  two last days (one for each of the two last days).

After all required fields will be filled, click on the ``[Save]`` button.

All databases with their settings are available in the ``[[ Backups ]] >> Configuration >> Dashboard`` section.
Each database specified in these settings will be presented in the dashboard.

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__

Usage
=====

Open the menu ``[[ Backups ]] >> Dashboard``

Top window is a general statistics of all your backups are stored on a remote server.

.. todo:: Add a description of top window when interfaces are ready.

Below are the forms for managing and controlling backups of your databases.
In addition to auto backup, you can make new backup manually at any time.
Backups taken by hand are not involved in auto rotation conditions.

.. todo:: Add the section when interfaces are ready.

{Instruction for daily usage. It should describe how to check that module works. What shall user do and what would user get.}

* Open menu ``{Menu} >> {Submenu} >> {Subsubmenu}``
* Click ``[{Button Name}]``
* RESULT: {what user gets, how the modules changes default behaviour}
