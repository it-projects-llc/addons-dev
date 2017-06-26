====================
 Real Multi Website
====================

Allows to set up multi-website and handles requests in a different company context. Later is especially useful for eCommerce to make orders for a different companies.

Odoo is designed to switch website by host name, but this feature is not completed and not supported. This module fills the gap.

Implementation
==============

Websites
--------

To work with ``website`` model, the module adds menu ``Website Admin >> Configuration >> Websites``.

Website Menus
-------------

To easy work with ``website.menu`` model, the module adds menu ``Website Admin >> Configuration >> Website Menus`` and adds form view.

eCommerce
---------

The main idea is creating different *public* users per each company instead of single *Public User* as it's used by default.


.. TODO check this note.
.. For authenticated users the module just changes user's company. It may lead to often database requests. See Usage Instruction how to avoid that.

Roadmap
=======

* Currently, all websites share the same theme. Possible solution to implement:

  * add many2many field website_ids to ``ir.ui.view``
  * rewrite ``get_inheriting_views_arch`` 

    * filter out views with non empty  website_ids and current website is not in website_ids
    * get website from context.
    * take care about context -- inherit render in ir.ui.view and update context if website_enabled (see module website)

  * rewrite ``theme_customize_get`` and ``theme_customize`` controllers and use both active and website_id fields to work with theme status

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
