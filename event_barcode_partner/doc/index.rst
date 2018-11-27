====================================
 Customised Event Barcode Interface
====================================

Installation
============
{Instruction about things to do before actual installation}

* {OPTIONAL }`Activate longpolling <https://odoo-development.readthedocs.io/en/latest/admin/longpolling.html>`__ 
* {Additional notes if any}
* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

* In order to use E-Sign feature be sure to provide a request template in event form

Usage
=====



* Open menu ``[[ Events ]]``
* Select an event
* Click on *Barcode Interface* Button in the header of thr form

* On another device open menu ``[[ Events ]]`` >> EST Session
* Select the event according to the *Barcode Interface* event in ``Event`` field
* Type the number of the opened *Barcode Interface* in the ``Barcode Interface Number`` field
* Click ``Open``

* In the *Barcode Interface* device Scan barcode or paste it into the top input, or start to type a name of an attendee in the bottom input
* Click on the required attendee
* in unfolded pop-up click *Send Request*

* In *EST Session* device you will see the request for sign
* Let the attendee sign here
* Click *Submit Sign*

* In the *Barcode Interface* you will see the notification that terms are signed
* Scan *RFID*
* Click ``Accept``

* Customer Attendeed
