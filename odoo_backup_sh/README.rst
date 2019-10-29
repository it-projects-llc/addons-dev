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

Manual Testing
==============

To test odoo_backup_sh* modules one can use following scenarios:

Test: rotation
--------------

* use database with demo
* install ``odoo_backup_sh``
* click ``[Get S3 storage]``
* configure any backup schedule
* configure rotation to test
* go to Dashboard and click *Update Info*
* check that backups are rotated according to plan

Preparation: Install base module
--------------------------------

* use database without demo
* if you previously installed backup modules, then uninstall them and delete ``odoo_backup_sh.*`` params in ``[[ Settings ]] >> System Parameters``. 
* install ``odoo_backup_sh``


Test: IAP S3
------------


* Install base module
* Click ``[Get S3 storage]``
* Create Schedule for current database. Test from this step should be proceeded in two different scenarios: with encryption disabled and enabled
* Test according to *Checklist: Backups*

Restoring without downloading:

* In new incognito window open ``/web/database/manager``
* In ``Odoo-backup.sh`` section restore database
* Login to the restored database -- all scheduled backuping must be disabled

Checklist: Backups
------------------

* Directly at the storage: create manually any file with random name
* Go to ``[[ Settings ]] >> Automation >> Scheduled Actions``

  * Find a cron job for backuping and click ``[Run Manually]``

* Go to ``[[ Settings ]] >> Backups``

  * Find just created backup
  * Click ``[Download]``
  * If database is encrypted, decrypt it as described in  `<doc/index.rst>`_
  * Restore database in a usual way

* Go to Dashboard
* Click ``[Make backup now]``
* Download the backup again as described above

Test: Dropbox only
------------------
* *Install base module*
* Install ``odoo_backup_sh_dropbox`` module
* Configure dropbox according to the module's documentation
* Create Schedule for any database
* Test according to *Checklist: Backups*

Test: All storages
------------------
* *Install base module*
* Install ``odoo_backup_sh_dropbox`` module
* Install ``odoo_backup_sh_google_disk`` module
* Configure all storages
* Create Schedule for the same database for all storages
* Test according to *Checklist: Backups*

Test: IAP Notification
----------------------

TODO

Test: IAP Credits
-----------------

TODO: Check purchasing, top-up, using credits, running out of credits

Credits
=======

Contributors
------------
* `Stanislav Krotov <https://it-projects.info/team/ufaks>`__
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support
      you are kindly requested to purchase the module
      at `odoo apps store <https://apps.odoo.com/apps/modules/12.0/odoo_backup_sh/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/misc-addons/12.0

HTML Description: https://apps.odoo.com/apps/modules/12.0/odoo_backup_sh/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 12.0 483b6024cd44fcc6e2b987505beb739014b51856
