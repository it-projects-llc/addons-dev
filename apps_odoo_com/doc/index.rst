====================================
 Odoo App Store administration tool
====================================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

To use this module, you need to have a password in ``apps.odoo.com`` database.

* Step 1. Ask support team to set some temporar password on apps.odoo.com database
* Step 2. Login to https://apps.odoo.com/web in a usual way (via oauth)
* Step 3. Open browser console and change password by using js code below

  .. code:: js

      odoo.define('www', function(require) {
      "use strict";
      var ajax = require('web.ajax');
      // will only work after the password has been set by Odoo
      ajax.jsonpRpc('/web/session/change_password', 'call', {
          'fields' : [
               {'name': 'old_pwd', 'value': 'demoo'},
               {'name': 'new_password', 'value': 'demooo'},
               {'name': 'confirm_pwd', 'value': 'demooo'}
           ]})
      .then(function(o) { console.log(o); });
      });

* Step 4. At your odoo database:

  * install this module and go to menu ``Odoo App Store >> Settings``
  * set login and password
  * click ``[Apply]``

Usage
=====

Scan Repo
---------

To call ``[Scan Repo]`` button

* go to ``Odoo App Store >> Tools >> Scan Repo``
* set ``Repository``
* click ``[Scan Repo]``

Adding batch of Repos
---------------------

* go to ``Odoo App Store >> Tools >> Add Repos``
* set ``Version``
* specify list of repos
* click ``[Add Repos]``
* RESULT: it will create and validate the repos. Errors are printed to odoo logs
