.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

================
 Odoo-backup.sh
================

The application allows managing database backups via a cloud, without a need to download and upload archive via a browser.

In-App Purchase
===============

The service **Odoo-backup.sh** provides a way to store backups in a cloud. Payments for the service is managed by propietary module, which implements `In-App Purchase <https://www.odoo.com/documentation/11.0/webservices/iap.html>`_ -- payments platform provided by *Odoo S.A.*.

Personal cloud
==============

TODO: this part is not implemented yet.

Additionally to the cloud provided by **Odoo-backup.sh** it's possible to store backups on a personal cloud. In that case user has to arrange credentials himself. Supported cloud providers and protocols are as following:

* TODO Dropbox
* TODO Google Drive
* TODO S3
* TODO Yandex.Disk
* TODO ftp

Posibility of using personal cloud *only* can be unlocked by purchasing module `odoo_backup_sh_private <https://apps.odoo.com/apps/modules/11.0/odoo_backup_sh_private/>`_

Implementation details
======================

/web/database/backups
---------------------

It's a new page in *database manager*, that allows to see list of available backups that can be restored. The process of receiving backup list is as following:

* *Browser* sends request to ``/web/database/backups``
* *Odoo instance* sends request to ``odoo-backup.sh/web/backup/list`` with ``user_key`` from odoo config file (it's generated automatically if it's not set).
* ``odoo-backup.sh`` **either** returns backup list and then browser shows backup list, **or** ``odoo-backup.sh`` doesn't recognise ``user_key`` and starts process of authentication via ``odoo.com`` as auth provider:

  * ``odoo-backup.sh/web/backup/list`` returns a link to redirect browser
  * *Browser* recieves from *Odoo instance* an html page that only redirects *User* to a technical page page in ``odoo-backup.sh``, which finally redirects *User* to ``odoo.com`` website
  * *User* enters his login-password and redirects back to a technical page in ``odoo-backup.sh`` from where he is redirected again to ``/web/database/backups`` page and the process starts again, but this time  ``odoo-backup.sh`` recognise ``user_key``
  


Credits
=======

Contributors
------------
* `Stanislav Krotov <https://it-projects.info/team/ufaks>`__

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/misc-addons/11.0

HTML Description: https://apps.odoo.com/apps/modules/11.0/odoo_backup_sh/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 11.0 71d5425c83edd212b4acf00f1d55bd5ee5f96761
