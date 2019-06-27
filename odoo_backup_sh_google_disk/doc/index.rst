=========================
 Backups to Google Drive
=========================

Installation
============

* Install `Google API Client Library for Python <https://developers.google.com/api-client-library/python/>`__ ::

    pip install google-api-python-client

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

Creating a Service Account Key
------------------------------

*Note: You need to have a Google account*

* Open the `GCP Console. <https://console.cloud.google.com/>`__
* Login into your Google account
* Press `Projects` button on the Top menu
* In Popup window choose `New Project`
* Define the Name and Location (if needed) of Project
* Click on `Create` button
* In Top menu choose your New project
* Open navigation menu (*Burger menu in the Left corner*)
* Choose APIs and ``[[Services]] >> Library``
* Choose Google Drive API and turn it on
* Go to `Service account` inside *IAM& admin*
* Click on `Create` and add the Private key
* Choose `Service account` or create a new one
  * If you create a new one please define ``[[Project]] >> Owner``
  * Define the name of Service account
  * Start Odoo with ``--load=web,odoo_backup_sh`` or set the ``server_wide_modules`` option in the Odoo configuration file
* Define a key type as *JSON*
* Click `Create` (key is created automatically)
* In opened page *IAM& admin* click on `Service account`
* Remember the e-mail of your service account

Access rights to Google Folder
------------------------------

* Go to `Google Drive <https://www.google.com/drive/>`__
* Create a new folder `Backups`
* Click the right mouse button on this folder and choose `Share+`
* In Pop up window fill in e-mail of created service account
* Confirm your action

Installation of Private key on server
-------------------------------------
In the Example below you can see the Server, which is launched with Docker

* Copy this path to the Docker container::

  docker cp PATH_FROM/YOU_FILE_NAME.JSON CONTAINER_NAME:/PATH_TO


Server Deployment
-----------------

* Activate `Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Go to ``[[Backups]] >> Configuration >> Settings``
* Choose Google Drive
* Click on `Save`

Usage
=====

* Open the menu ``[[ Backups ]] >> Dashboard``
* Proceed with ``[[ Backups ]] >> Backups`` where Google drive databases are presented
* ``[[ Backups ]] >> Backups``
* Go to ``[[Backup]] >> Configuration >> Schedules and Rotations``
* See ``[[Backup]] >> Notifications`` if new one is displayed


RESULT: You can see the main Graph with the general statistics of all your backups are stored on a remote server. After this window a special form for managing and controlling backups of your databases specially *for Google drive* is located.
In addition to auto backup, you can make new backups manually at any time. Backups *taken by hand* are not involved in auto rotation conditions.


