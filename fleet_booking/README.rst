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

-----------------------
 Vehicle Rental Prcess
-----------------------

One model ``fleet_booking.rental`` is used for working with different types of rental documents:
The types of document are ``Rent``, ``Extended Rent``, ``Return``.
Each type of the documents has several states.
``Rent`` has the states that are ``Quotation``, ``Booked``, ``Confirmed``, ``Close``.
``Extended Rent`` has the same statuses as ``Rent``.
``Return`` may be ``Quotation``, ``Confirmed`` or ``Close``.

All rental views are grouped under ``Fleet Rental``. There are the following items available for
a user.

 * Rental Quotations
 * Rental Orders
 * Retrun Quotations
 * Return Orders
 * All confirmed documents

Under ``Rental Quotations`` are ``Rent`` and ``Extended Rent`` documents with ``Quotation`` or ``Booked`` states.
After confirmation they are available uder the ``Rental Orders``.

Under ``Ruturn Quotations`` are ``Return`` documents that are not confirmed yet.
After confirmation they are available under ``Return Orders``.

Buttons
^^^^^^^

Buttons ``[Book Only]``, ``[Confirm]``, ``[Return]``, ``[Extend]`` are available in
Rental Quotation. There is no ``[Extend]`` for ``Extended Rent``.

Only booked or confirmed rents are visible on the calendar view of the documents form.

The ``[Confirm Rental]`` and ``[Book Only]`` buttons change the state of existing records.
``[Confirm Rental]`` is only enabled if all fields related to payment are filled.

``[Print Rental Agreement]`` and ``[Create Invoice]`` buttons become enabled after confirmation on Rentals and Returns.
Whe a document has related invoices then ``[Invoices]`` button become visible.

A new record with type ``[Extended Rent]`` is created when a user clicks ``[Extend]`` button on a Rental Quotation from view.
Also a new record with type ``[Return]`` is created when a user clicks ``[Return]`` button.
Confirmed quotations become visible on the calendar view.


Further information
-------------------

HTML Description: https://apps.odoo.com/apps/modules/9.0/fleet_booking

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 9.0 d3dd4161ad0598ebaa659fbd083457c77aa9448d
