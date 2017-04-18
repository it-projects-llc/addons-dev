===================
 Website sale cache
===================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__

Configuration
=============

The module does not need to be pre-configured.


Usage
=====
When category display is activated, module immediately begins to cache the product categories,
significantly speeding up the loading of the page.

The speed increase will be absent at the first load, because the data has not yet been cached. Also when updating
the list of categories (deleting a category, updating or creating a new one), the cache will be updated, which will also
cause an absent of speed increase at the first load after making changes.

Demo: http://runbot.it-projects.info/demo/mail-addons/9.0

HTML Description: https://apps.odoo.com/apps/modules/9.0/website_salecache/
