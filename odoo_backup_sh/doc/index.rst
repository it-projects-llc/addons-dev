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

To appear desired databases in the backup dashboard, you have to set up settings for it.

* Open the menu ``[[ Backups ]] >> Dashboard``.
* Click on the ``[Add Database]`` button in the dashboard header.
* Fill required fields:

    * Database: select one of your databases

    * Auto Backup Execute Every:  type a value and select a unit of measure.

*Example: You want the module to make new backup every 2 hours. If you want to create backups manually only, leave this field blank.*

    * Next Execution Date: It shows next planned auto backup date. You can correct this.

*Example: You want the module to make new backup every day at night time.*

    * Auto Rotation: If you have set up the auto backup, you can specify how many backups to preserve for certain time frames.

*Example: The module makes auto backup your database every 2 hours. You want to preserve 2 daily backups and 1 weekly only.Set up Daily and Weekly rotation options as Limited and put the numbers in limit fields.*

* All other options mark as **Disabled**.

After all required fields will be filled, click on the ``[Save]`` button.

All databases with their settings are available in the ``[[ Backups ]] >> Configuration >> Dashboard`` section.

Each database specified in these settings will be presented in the dashboard.

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__

Usage
=====

* Login into your `Odoo account <https://www.odoo.com/web/login>`__
* Click on ``Create Database`` button
* In the open Pop-up window enter *Master Password*, fill required information such as Phone number, Language, Country, Password
* Provide the name for Database
* Click on ``Continue`` button

RESULT: Backup is created.
*The manual database creation may take some time before being ready*.

* Login into your `Odoo account <https://www.odoo.com/web/login>`__
* Click on ``Restore via Odoo-backup.sh`` button
* Choose the backup that you want to restore
* In the open Pop-up window enter *Master Password*, fill the *Database Name*
* Click on `Restore` button

RESULT: Backup is restored without any additional manipulations such as *downloading-uploading* process.
*The database restore may take some time before being ready*.

* Login into your `Odoo account <https://www.odoo.com/web/login>`__
* Click on ``Restore`` button
* Upload file that you want to restore
* Think up the Database Name
* In order to avoid conflicts between databases, choose the option if this database was moved or copied.
* In the open Pop-up window enter *Master Password*, fill the *Database Name*
* Click on `Continue` button


RESULT: Backup is restored.
*The database restore may take some time before being ready*.

