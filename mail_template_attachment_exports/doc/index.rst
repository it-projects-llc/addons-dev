====================
 Exporting by Email
====================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

Configuring Email Template
--------------------------

Create field list

* Open a menu with records you are going to export and attach in email. For example ``Settings >> Users >> Users``
* Switch to list view
* Select any Record
* Click ``Action -> Export``
* Select fields you want to export, for example ``Name``, ``Latest connection``
* Click **Save fields list**
* Set any name (e.g. ``Latest connection``) you like and click ``[Ok]``

Configure Email Template

* `Enable technical features <https://odoo-development.readthedocs.io/en/latest/odoo/usage/technical-features.html>`__
* Open menu ``Settings >> Technical >> Email >> Templates``
* Open or create new Record
* Pay attention on **Applies to** field. You will need it on sending. If you create new Record, set it to ``Partner``, for example.
* At ``Advanced Settings`` tab specify at ``Exporting Section``:

  * **Model**, e.g. ``Partner``
  * **Domain**, e.g. ``Phone is Set``
  * **Fields** - one you created previously, e.g. ``Latest connection``
  * **Export Format** - ``CSV`` or ``Excel``

* After saving\creating Record pay attention on Record id (it can be found in page url). Record id may be needed for sending email.

Sending email
-------------

Option 1. Manual email sending.

* Open menu with records specified in **Applies to** field. For example, menu ``Contacts``
* Open some record
* Click ``[New message]`` button
* Click Edit icon to open Mail Composer
* Specify template with Exporting in **Use template** field
* Click ``[Send]``
* Email with export data is sent. You can find it in messaging section of the record

Option 2. Periodic email sending.

* Open menu ``Settings >> Technical >> Automation >> Scheduled Actions``
* Click ``[Create]``
* Set **Name**, e.g. ``Notify on latest connections``
* On ``Information`` tab specify periodicity, e.g.

  * **Interval number** is ``1``
  * **Interval Unit** is ``Days``
  * **Number of Calls** is ``-1`` (unlimited)

* On ``Technical data`` tab set

  * **Object** is TODO
  * **Method** is TODO
  * **Arguments** is ``(ID,)``

* Click ``[Save]``

Option 3. Send email with exporting on updates.

* Install ``Automated Action Rules`` module (technical name ``base_action_rule``)
* Create server action

  * Open menu ``Settings >> Technical >> Action >> Server Actions``
  * TODO

* Create Automated Action

  * Open menu ``Settings >> Technical >> Automation >> Automated Actions``
  * TODO
