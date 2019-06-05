=========================
 Backups to Google Drive
=========================

Installation
============

* Install `Dropbox for Python SDK <https://www.dropbox.com/developers/documentation/python#install>`__ ::

    pip install dropbox

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

Creating Access Token
---------------------

Note: You need to have a Dropbox Account

* Open the App Console. https://www.dropbox.com/developers/apps
* Login to Dropbox.
* Click `Create app`
* Choose an API e.g. `Dropbox API`
* Choose the type of access e.g. `App folder`
* Specify name of your app e.g. `Odoo Backups`
* Accept the agreement
* Click `Create app`
* Click to `Generate` to Generated access token
* Save the access token

Folder in Dropbox
-----------------

* Open your Dropbox https://www.dropbox.com/home/
* Open Applications >> Odoo Backups
* Create new folder "Backups"

Config Settings
---------------

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Open menu Backups >> Configuration >> Settings
* Specify Dropbox
* Click to Save
* Specify "Dropbox Access Token"
* Specify your folder path "/Backups"
* Click to Save

Usage
=====

TODO: Usage
