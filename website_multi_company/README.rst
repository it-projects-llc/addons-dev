====================
 Real Multi Website
====================

Allows to set up multi-website and handles requests in a different company context. Later is especially useful for eCommerce to make orders for a different companies.

The module switches  context (website and company) depending on a request host. Only one context is available per host. Manual selection of a website+company by user is not supported.

The main idea is to create different *public* users per each company instead of single *Public User* as it's used by default.

For authenticated users the module just changes user's company. It may lead to often database requests. See Usage Instruction how to avoid that.

Credits
=======

Contributors
------------
* Ivan Yelizariev <yelizariev@it-projects.info>

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/website-addons/10.0

HTML Description: https://apps.odoo.com/apps/modules/10.0/website_multi_company/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 10.0 {ODOO_COMMIT_SHA_TO_BE_UPDATED}
