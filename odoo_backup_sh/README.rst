.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

================
 Odoo-backup.sh
================

The application allows managing database backups via a cloud, without a need to download and upload archive via a browser.

In-App Purchase
===============

The service **Odoo-backup.sh** provides a way to store backups in a cloud. Payments for the service is managed by proprietary module, which implements `In-App Purchase <https://www.odoo.com/documentation/11.0/webservices/iap.html>`__ -- payments platform provided by *Odoo S.A.*.

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

It's a new page in *database manager*, that allows to see list of available backups that can be restored. A process of receiving backup list is described below. Click on the ``Restore via Odoo-backup.sh`` consists the following operations:

* If there are not amazon S3 credentials in the config file, the module makes requests to get them:

  * *Browser* sends request to ``/web/database/backups``
  * *Odoo instance* sends request to ``odoo-backup.sh/get_cloud_params`` with ``user_key`` from odoo config file (the ``user_key`` is generated automatically if it's not set).
  * ``odoo-backup.sh`` **either** returns amazon S3 credentials with which the module can use to send request to S3 independently, **or** ``odoo-backup.sh`` doesn't recognise ``user_key`` and starts process of authentication via ``odoo.com`` as auth provider:

    * ``odoo-backup.sh/get_cloud_params`` returns a link to redirect to odoo.com authentication page
    * *User* enters his login-password and is redirected back to ``/web/database/backups`` page and the process starts again, but this time ``odoo-backup.sh`` recognise ``user_key`` and return amazon credentials

* If amazon S3 credentials are in the config file, the module makes request to AWS S3 to get list of users backups and then renders it.

Dashboard menu item in the Backups section
------------------------------------------

It's a page where an user can watch detail information about his backups which are remote stored. Also he can make backup of any his database. This backup will be sent to AWS S3 for storing. Moreover the user can create autobackup settings. The settings say to the module at what point of time, from which databases to create backups and max number of backups of database must be store.

When the user opens the backups dashboard, the module makes similar requests are described above about /web/database/backups page.

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
