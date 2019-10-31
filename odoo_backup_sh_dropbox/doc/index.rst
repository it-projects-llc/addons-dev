====================
 Dropbox backing up
====================

Installation
============

* Install `Dropbox for Python SDK <https://www.dropbox.com/developers/documentation/python#install>`__ ::

    pip install dropbox

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

Creating Access Token
---------------------

*Note: You need to have a Dropbox account*

* Open the `App Console <https://www.dropbox.com/developers/apps>`__
* Login/Register into Dropbox account.
* Click on `Create app`

.. image:: create-app.png

* Choose an API e.g. `Dropbox API`
* Choose the type of access e.g. `App folder`
* Specify the name of your App e.g. `Odoo Backups`
* Read and accept the agreement
* Click on `Create app` button
* Click on `Generate` button in order to Generated access token
* Save the access token

Folder in Dropbox
-----------------

* Open your `Dropbox <https://www.dropbox.com/home/>`__
* Open Applications >> Odoo Backups
* Create new folder "Backups"

Config Settings
---------------

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Open menu ``[[Backups]] >> Configuration >> Settings``
* Choose Dropbox option
* Click on `Save` button
* Specify *Dropbox Access Token*
* Specify your folder path `/Backups`
* Click on `Save` button

Usage
=====

**Create:**

* Open the menu ``[[ Backups ]] >> Configuration >> Settings``
* Choose the Dropbox and click on ``Save`` button
* Enter *Dropbox Access Token*
* Enter *Dropbox Folder Path*
* Click on ``Save`` button
* Set up a new configuration  [[ Backups ]] >> Dashboard >> Add Database
* Choose the Database in the database field
* Define the Storage service
* Encrypt your backup if you need, but do not forget the password
* Enter *Interval Number*, *Interval Unit*, *New execution Date*
* Select/unselect *"Active" checkbox*
* Click on ``Save`` and come back to set up the feature
* Go to ``[[ Backups ]] >> Dashboard``
* Click on ``New Backup`` in the appeared configuration

RESULT: Backup is stored in the Dropbox cloud.
*The manual backup creation may take some time before being ready*.

.. note::
   Restore without additional downloading is available only for* `Odoo backup service <https://apps.odoo.com/apps/modules/12.0/odoo_backup_sh/>`__

**Visualize:**

* Open the menu ``[[ Backups ]] >> Dashboard``
* Proceed with ``[[ Backups ]] >> Backups`` where *Odoo-backup.sh* databases are presented
* Continue with ``[[ Backups ]] >> Backups`` where your Odoo backups are stored

RESULT: You can see the main Graph with the general statistics of all your backups are stored on a remote server.
After this window a special form for managing and controlling backups of your databases specially *for Dropbox* is located.

