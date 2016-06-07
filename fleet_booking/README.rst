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

------------------------
 Vehicle Rental Process
------------------------

One model ``Rental`` is used for working with different rental forms that are:

 * Rental Quotations
 * Rental Orders
 * Extended Rental Orders
 * Return Orders

Rental functions are grouped under ``Fleet Rental`` menu.

Workflow and buttons
^^^^^^^^^^^^^^^^^^^^

**Quotation -> Quotation Booked**
A Quotation goes to the ``Quotation Booked`` state when a user clicks ``[Book Only]`` button on a Rental Quotation form view.
``[Book Only]`` button is only enabled when the ``Edit Date`` and ``Return Date`` fields are filled.
Booked quotations become visible on the calendar view of the ``Rental`` model.

**Quotation -> Rental Order**, **Quotation Booked -> Rental Order**
A Quotation goes to the ``Rental Order`` state when a user clicks ``[Confirm Rental]`` button on a Rental Quotation from view.
``[Confirm Rental]`` is only enabled if all fields related to payment are filled.
Confirmed quotations become visible on the calendar view.
``[Print Rental Agreement]`` button become enabled.
``[Create Invoice]`` button become enabled. 

When invoices are created on a Rental the ``[Invoices]`` smart button become visible on a Rental Order form view.
