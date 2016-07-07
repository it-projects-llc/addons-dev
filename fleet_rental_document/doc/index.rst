=======================
 Fleet Rental Document
=======================

Usage
=====

Create items for checklists
---------------------------

* Open menu ``Sales / Configuration / Rental / Vehicle items to check`` 
* Click on ``[create]`` button to create an item. For example, Oil
* Create as many items as you need

Vehicle Rental Information
--------------------------

* Open ``Fleet / Vehicles`` menu
* Under ``Rental Properties`` group for each vehicle define the following information:

 * Daily rental price
 * Rate per extra km
 * Allowed kilometer per day

Based on these values, Total Rental price will be automatically calculated in all documents.

Rent documents
--------------

* Open menu ``Sales / Rental / Rent [document state]`` 
* Click ``[create]`` button to create new Rent document. New documents get initial status that is Draft.
* Fill all required fields on the form and click ``[Book Only]`` if you haven't received deposit payment from your client.
* Click ``[Cancel Booking]`` if you want to cancel it.
* If the deposit is paid click ``[Confirm Rental]`` button.
* Submenus are available to work with rent documents in three different states:

 * ``Rent Draft``
 * ``Rent Booked``
 * ``Rent Confirmed``

* Open ``Sales / Rental / Rent Draft`` to book or confirm rents.
* Open ``Sales / Rental / Rent Booked`` to confirm or cancel booking.
* Open ``Sales / Rental / Rent Confirmed`` to extend rents or create return documents on them.

Return documents
----------------

* Open menu ``Sales / Rental / Rent Confirmed``
* Filter Return documents to show only those that not in ``returned`` or ``extended`` states
* Search by Agreement Number or Car Plate Number the Rent Document
* Open it
* Click ``[Return]`` button to create new Return document. New documents get initial status that is Draft.
* Fill all required fields on the form and click ``[Confirm Return]`` to confirm
that the vehicle is returned and cleint has paid all sum for the rent.
* Click ``[Return car and Keep contract Open]`` to confirm that the
vehicle is returned.
* Submenus are available to work with Return documents in three different states:

 * ``Return Draft``
 * ``Return Open``
 * ``Return Closed``

* Open ``Sales / Rental / Return Draft`` to see Return documents that are waiting for your action
* Open ``Sales / Rental / Return Open`` to see Return documents where rent isn't fully paid
* Open ``Sales / Rental / Return Closed`` to see Return documents where rent is fully paid or where
excess amount of deposit should be returned to a customer
