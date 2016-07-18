==============
 Fleet Rental
==============


Preparation
===========

Administrator must set appropriate branches for every user that needs to have branch-based limitations.

General Manager must create items for checklist.

Vehicle support officer must create vehicles and fill it with valid information.

Create items for checklists
---------------------------

* Open menu ``Sales / Configuration / Rental / Vehicle items to check``
* Click on ``[create]`` button to create an item. For example, Oil
* Create as many items as you need

Vehicle Rental Information
--------------------------

* Open ``Fleet / Vehicles`` menu
* Set vehicle current branch.
* Under ``Rental Properties`` group for each vehicle define the following information:

 * Daily rental price
 * Rate per extra km
 * Allowed kilometer per day

Based on these values, Total Rental price will be automatically calculated in all documents.


Usage
=====

Access rights and duties
------------------------

All rental documents duties assigned to Branch Officer.


Definitions
-----------

* Rent - basic rental document to register vehicle rent. Here is represented main information about rent.
    From this document you can access any others subordinated documents (invoices, extends, return).
* Extend - optional document for cases when customer wished to extend vehicle rental period.
* Return - mandatory document for registering of vehicle transfer from customer back to company fleet.
    In return document calculates extra payments for mileage and time excess and all other mutual settlements.
* Invoice - document reflecting fact of some debt. It may be customer debt for vehicle rent, or company debt (when refund needed).
    Invoice might be paid by bank or cash. Payment reduces debt.

Rental workflow
---------------

Simplified workflow is like that:

 * Create rent.
 * Create invoice and register payment.
 * Create extend if needed.
    * Create invoice for it and register payment.
 * Create return document.
    * Create invoice for extra stuff (mileage, time) and register payment.
    Or
    * Create refund if customer does not spent all his balance and register payment.


Detailed description of the documents usage
-------------------------------------------

Rent
----

* Create new rent document.
* Select customer.
* Select vehicle. In selection you will see only *active* vehicles belonging to your branch.
    Before picking vehicle make sure it ``Rental Properties`` filled correctly.
* After vehicle is picked you will see that most document fields filled automatically.
* Set ``Original return time`` and other necessary data.
* Go down to ``Vehicle Checklist`` and mark all lines according to it current state.
* Go further down to vehicle scan. Press parts of that scan to mark some with red colour.
* Save document.
* When everything is ready press ``[Book only]``. That makes this document and vehicle status turns to ``Booked``.
* Press ``[Create invoice]``. On first occurrence you have to chose account for customers deposits.
    Pick ``246000 Customer Deposits Received`` or any other account suitable for yours company accounting chart.
* Enter ``Down Payment Amount`` and press ``[Create and View Invoices]``. Created invoice document form will appear.
* Press ``[Validate]`` to register customer debt.
    Now you may turn back to rent document to look up ``Balance``
* Press ``[Register payment]`` after you got bankroll from customer.
    * Select either ``Bank`` or ``Cash`` payment method and validate payment.

Extend
------

* Open rent document to be extended.
* Press ``[Extends]`` button (smart button with book picture in upper right part of document).
* Press ``[Create]`` to create new extend document.
* Some fields is filled automatically and cant be changed.
* Enter new ``Return Date and Time``. Consider that ``Exit Date and Time`` is taken from main rent document.
    Thereby ``Total Rental Period`` in this document equal to total days, starting from main rent document ``Exit Date and Time`` to that extend's ``Return Date and Time``.
    It is concerns all other ``Payment Details`` fields.
* Enter other necessary fields.
* Press ``[Submit]``.
* Create and validate invoice.
* Register payment.
* Press ``[Confirm rental]`` to confirm extend document.
* In main rental document you will see ``Extended return time`` field changed and equal to ``Return Date and Time`` of **last** extend document.
    Also ``Advanced Deposit`` and ``Balance`` fields always displays total sum per all subordinated documents payments.

Return
------

* Open rental document for which you need create return.
* Press ``[Create Return Document]``. You'll be able to see this button only if state of rent document is ``Confirmed`` or ``Extended``.
* Return document form will be opened.
* Set ``Odometer after Rent``. If there is some mileage excess then ``Extra Kilos Charge`` will be accordingly counted.
* Set ``Return Date and Time``. If there is some time excess takes place then ``Extra Hours Charge`` will be accordingly counted.
* Fill up ``Vehicle Checklist`` using ``on return`` columns.
* Press ``[Return car and keep contract open]``.
* If mutual installments and vehicle condition is ok, then just press ``[Save]`` and vehicle rent lifecycle is finished there.
* If there is some divergency in mutual installment then create invoice/refund according to what you need by pressing ``[Create invoice]`` or ``[Create refund]``.
    * Validate payment for created document,



