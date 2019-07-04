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

* To appear desired databases in the backup dashboard, you have to set up settings for it:

  * Open the menu ``[[ Backups ]] >> Dashboard``.
  * After redireсtion please login in `Odoo.com <https://www.odoo.com/web/login>`__
  * Click on the ``[Add Database]`` button in the dashboard header.
  * Choose the Database in the database field
  * Encrypt your backup if you need, but do not forget the password
  * Fill required fields:

    * **Database:** select one of your databases

    * **Auto Backup Execute Every:**  type a value and select a unit of measure.

      *Example: You want the module to make new backup every 2 hours. If you want to create backups manually only, leave this field blank.*

    * **Next Execution Date:** It shows next planned auto backup date. You can correct this.

      *Example: You want the module to make new backup every day at night time.*

    * **Auto Rotation:** If you have set up the auto backup, you can specify how many backups to preserve for certain time frames.

      *Example: The module makes auto backup your database every 2 hours. You want to preserve 2 daily backups and 1 weekly only.Set up Daily and Weekly rotation options as Limited and put the numbers in limit fields.*

    * All other options mark as **Disabled**.

* After all required fields will be filled, click on the ``[Save]`` button.

* All databases with their settings are available in the ``[[ Backups ]] >> Configuration >> Dashboard`` section.

* Click on ``New Backup`` in the appeared configuration

* Each database specified in these settings will be presented in the dashboard.

Usage
=====

Manual creation of backups:

* Open the menu ``[[ Backups ]] >> Dashboard``
* After redireсtion please login into your `Odoo account <https://www.odoo.com/web/login>`__
* Set up a new configuration  [[ Backups ]] >> Dashboard >> Add Database
* Choose the Database in the database field
* Encrypt your backup if you need, but do not forget the password
* Enter *Interval Number*, *Interval Unit*, *New execution Date*
* Select/unselect *"Active"* checkbox
* Click on ``Save`` button
* Go to ``[[ Backups ]] >> Dashboard``
* Click on ``New Backup`` in the appeared configuration

RESULT: Backup is created.
*The manual backup creation may take some time before being ready*.


Restoration:
* Please proceed to the Database Manager: ``/web/database/manager``
* Click on ``Restore via Odoo-backup.sh`` button
* Choose the backup that you want to restore
* In the open Pop-up window enter Master Password, fill the Database Name*
* In order to avoid conflicts between databases choose if this database was moved or copied*
* Click on ``Continue`` button

RESULT: Backup is restored in one click without any additional manipulations such as "downloading-uploading process".
*The database restore may take some time before being ready*.

Visual presentation:
* Open the menu ``[[ Backups ]] >> Dashboard``
* Proceed with ``[[ Backups ]] >> Backups`` where *Odoo.sh* databases are presented
* Continue with ``[[ Backups ]] >> Backups`` where your Odoo backups are stored

RESULT:
You can see the main Graph with the general statistics of all your backups are stored on a remote server.

