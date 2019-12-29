==========================
 Register Event Attendees
==========================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

* Set POS to process events

    * Open menu ``[[ Point of Sale ]]>> Configuration >> Point of Sale``
    * Choose an existing POS or create a new one
    * Select or create an Event Set in the **Event** field
    * Set **Only Tickets** True if you want to see in POS only tickets

* Create **Event Set**

    * Specify **Name**
    * Add or create some **POS Ticket**

* Create **POS Ticket**

    * Select an Event in the field **Event**
    * Select a **Ticket**
    * Select a related **Product** to be shown in the POS as the ticket
    * Set **Mandatory RFID** To process attendee only if he is set RFID

Usage
=====

Proceed an Attendee
-------------------

* Open a POS with set Event
* In order to select an attendee do the next

    * Scan attendees ticket barcode
    * Click **Attendees** button and type attendees name into the search bar and then click on the necessary line

* In shown window you can see attendees details
* Scan a RFID to set it to the attendee
* Click **Attendeed** to process the attendee

Ticket sales
------------

* In POS sell a ticket to a customer like a regular product
* On the receipt screen as attendee is created a *Open Attendee* button is appeared, Click on it
* In opened Attendee screen you proceed an attendee as it is written above

RESULT: Attendees are processed and Tickets are sold out via POS
