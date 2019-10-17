.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

============
 S3 Backups
============

The 10 Euros service that would save your business.

In-App Purchase
===============

**odoo-backup.sh** provides a way to store backups in a cloud. Payments for the service is managed by proprietary module, which implements `In-App Purchase <https://www.odoo.com/documentation/12.0/webservices/iap.html>`__ -- payments platform provided by *Odoo S.A.*.

Personal cloud
==============

Additionally to the cloud provided by **odoo-backup.sh** it's possible to store backups on a personal cloud. In that case user has to arrange credentials himself. Supported cloud providers and protocols are as following:

* `Dropbox <https://apps.odoo.com/apps/modules/12.0/odoo_backup_sh_dropbox/>`_
* `Google Drive <https://apps.odoo.com/apps/modules/12.0/odoo_backup_sh_google_disk/>`_

*You need to get corresponding modules to use personal cloud.*

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

When the user opens the backups dashboard, the module makes similar requests are described above about ``/web/database/backups page``.

Roadmap
=======

* Config names should have prefix, e.g. ``odoo_backup_sh_``. Current names are ``amazon_bucket_name', 'amazon_access_key_id', 'amazon_secret_access_key', 'odoo_oauth_uid'``

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

      To get a guaranteed support
      you are kindly requested to purchase the module
      at `odoo apps store <https://apps.odoo.com/apps/modules/{VERSION}/{TECHNICAL_NAME}/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/misc-addons/12.0

HTML Description: https://apps.odoo.com/apps/modules/12.0/odoo_backup_sh/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 12.0 483b6024cd44fcc6e2b987505beb739014b51856
