=========================
 Google Drive backing up
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

Note: You need to have a Google account with activated access to `Google Cloud Platform <https://cloud.google.com/>`__.

* `Create new Project <https://console.cloud.google.com/projectcreate>`__ in Google Cloud 
* Switch to the created Project
* Open navigation menu (*Burger menu in the Left corner*)
* Choose ``API & Services >> Library``

  .. image:: api-library-menu.png

* Choose Google Drive API and turn it on

  .. image:: enable-api.png

* Open navigation menu (*Burger menu in the Left corner*)
* Choose ``IAM & admin >> Service accounts``

  .. image:: service-accounts-menu.png

* Click on ``+ CREATE SERVICE ACCOUNT`` and add the Private key

  * Set name, e.g. ``Odoo Backups`` and click ``[Create]`
  * At next the step set permission ``Project >> Owner``

    .. image:: service-account-permission.png

  * At the last stage click ``+ CREATE KEY``

    * Use key type ``JSON``

    .. image:: create-key.png

Access rights to Google Folder
------------------------------

* Go to `Google Drive <https://www.google.com/drive/>`__
* Create a new folder, say `Odoo Backups`
* Open folder and click `Share` button in folder menu

  .. image:: share-button.png

* In Pop up window fill in e-mail of created service account. It should have Edit access

  * You can find service account e-mail in Google Cloud in menu ``IAM & admin >> Service accounts``

* Confirm your action

  .. image:: share-folder.png

* Check URL in your browser. It has following format:
  ``https://drive.google.com/drive/folders/1oRL3sEKsk9i9Iripu7hsroaYpefl4DO4``,
  where last part is the *Folder ID*: ``1oRL3sEKsk9i9Iripu7hsroaYpefl4DO4``. You will need it later.

  .. image:: folder-id.png

Installation of Private key on server
-------------------------------------

TODO


Server Deployment
-----------------

TODO

* Activate `Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Go to ``[[Backups]] >> Configuration >> Settings``
* Choose Google Drive
* Click on `Save`

Usage
=====

Manual backups
--------------

.. this sections is a copy-paste from odoo_backup_sh/doc/index.rst

* Configure Backup Schedule as described above
* Open the menu ``[[ Backups ]] >> Dashboard``
* Click on ``[Make Backup now]``

RESULT: Backup is created. *Note, that the manual backup creation may take some time before being ready*

Backup Dashboard
----------------

.. this sections is a copy-paste from odoo_backup_sh/doc/index.rst

* Open the menu ``[[ Backups ]] >> Dashboard``

RESULT: You can see the main Graph with the general statistics of all your backups are stored on a remote server.
