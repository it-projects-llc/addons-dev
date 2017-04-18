==================
Website sale cache
==================

This module caches product public categories from module "website_sale". 
That allows to significantly accelerate the loading of the page with a large number of product categories.

Note
----
When used with multiple odoo workers, the cache is updated separately for each one. So the page may be load slowly until
the cache is updated for each worker. After the cache is updated for each worker, the page will load faster, as far as
the advantages of caching allow.

Warning
-------
Cache updates every time on creation, editing or deletion of instance product public category model.
That can cause problems as example when importing a large number of categories.
It is recommended to temporarily disconnect the module in such cases.

Credits
=======

Contributors
------------
* Artyom Losev <losev@it-projects.info>

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

Further information
===================
Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_
