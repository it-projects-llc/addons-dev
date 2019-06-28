====================
 Backups to Dropbox
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

* Open the menu ``[[ Backups ]] >> Dashboard``
* Proceed with ``[[ Backups ]] >> Backups`` where Dropbox databases are presented
* Go to ``[[Backup]] >> Configuration >> Schedules and Rotations``
* See ``[[Backup]] >> Notifications`` if new one is displayed

RESULT: You can see the main Graph with the general statistics of all your backups are stored on a remote server. After this window a special form for managing and controlling backups of your databases specially *for Dropbox* is located.
In addition to auto backup, you can make new backups manually at any time. Backups *taken by hand* are not involved in auto rotation conditions.