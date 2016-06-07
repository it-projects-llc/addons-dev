===============================
 Custom system for car renting
===============================


Adds roles:

    - Branch Officer
    - Vehicles Support Officer
    - Branch Employee
    - General Manager
    - Accountant
    - Payroll Officer


Adds branches in fleet module. Branches is stations between which cars are moved.

Adds partner personality info:

    - Date of birth (from partner_person module)
    - Nationality (from partner_person module)
    - Third Name
    - Family Name
    - ID Type
    - ID Number
    - Issuer
    - Date of Issue
    - License Type
    - License Number

Adds partner age restriction (must be 21 or elder) if he/she is customer (is customer field).

-------------------------
 Vehicle Rental Workflow
-------------------------

One model ``fleet_booking.rental`` is used for working with different types of rental documents:
The types of document are ``Rent``, ``Extended Rent``, ``Return``.
Each type of the documents has several states.
``Rent`` has the states that are ``Quotation``, ``Booked``, ``Confirmed``, ``Extended``, ``Returned``.
``Extended Rent`` has the same states: ``Quotation``, ``Booked``, ``Confirmed``, ``Extended``, ``Open Return``, ``Closed Return``.
``Return`` may be ``Return Draft``, ``Return Open``, ``Closed``.

All rental views are grouped under ``Fleet Rental`` top-level menu. There are the following submenu items available for
a user.

 * Rent Quotations
 * Confirmed Rents 
 * Draft Return Contracts
 * Open Return Contracts 
 * Closed Return Contracts 
 * All Records 

Under ``Rent Quotations`` are ``Rent`` and ``Extended Rent`` documents with ``Quotation`` or ``Booked`` states.
After confirmation they are available uder the ``Confirmed Rents``.

Under ``Draft Return Contracts`` are ``Return`` documents that are not confirmed yet.
After confirmation as closed they are available under ``Closed Return Contracts``.
After confirmation as open they are availbale under ``Open Return Contracts``.

Buttons ``[Book Only]``, ``[Confirm]``, ``[Return]``, ``[Extend]`` are available in
Rent Quotation.

The ``[Confirm Rental]`` and ``[Book Only]`` buttons change the state of existing records.
``[Confirm Rental]`` is only enabled if all fields related to payment are filled.

``[Print Rental Agreement]`` and ``[Create Invoice]`` buttons become enabled for Confirmed Rents.
When a document has related invoices then ``[Invoices]`` button become visible.
A user can click to it to see all related invoices.

A new record with type ``[Extended Rent]`` is created when a user clicks ``[Extend]`` button in Confirmed Rents. 
Also a new record with type ``[Return]`` is created when a user clicks ``[Return]`` button.


Further information
-------------------

HTML Description: https://apps.odoo.com/apps/modules/9.0/fleet_booking

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 9.0 d3dd4161ad0598ebaa659fbd083457c77aa9448d
