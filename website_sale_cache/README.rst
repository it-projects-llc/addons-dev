Website sale cache
=================

This module caches product public categories from module "website_sale". 
That allows to significantly accelerate the loading of the page with a large number of product categories.


Note
----
When you use multiple odoo workers, the cache is updated separately for each one. So the page may be load slowly until the cache is updated for each worker. After the cache is updated for each worker, the page will load faster, as far as the advantages of caching allow.

