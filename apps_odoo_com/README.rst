.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

======================
 Odoo App Store Admin
======================

Tool to work with apps.odoo.com database via xmlrpc. Usefull for sharing administration rights with your colleagues as well as for automation.

Configuration
=============

To use this module, you need to have a password in ``apps.odoo.com`` database.

* Step 1. Ask support team to set some temporar password on apps.odoo.com database
* Step 2. Login to https://apps.odoo.com/web in a usual way (via oauth)
* Step 3. Open browser console and change password by using js code below

  .. code::js
  
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


.. Known issues / Roadmap
.. ======================
.. 
.. * ...

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Ivan Yelizariev <yelizariev@it-projects.info>

.. Funders
.. -------
.. 
.. The development of this module has been financially supported by:
.. 
.. * Company 1 name
.. * Company 2 name

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
