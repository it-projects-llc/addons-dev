====================
 Multi Website Blog
====================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

* Create and configure websites according to the ``website_multi_company`` module documentation
* Open menu ``[[ Website ]] >> Blog >> Blogs``
* Set **Allowed Websites** select the websites your blog will be available on
* Open menu ``[[ Website ]] >> Configuration >> Menus``
* Make sure that there is a menu to open the blog

Usage
=====

* Open your blog on website
* Change url so it would lead to this blog from your another website - just change website-related part of the url leaving the same blog-related part
* Since your blog shouldn't be used from your another website - you should see a page with ``403: Forbidden`` on it
