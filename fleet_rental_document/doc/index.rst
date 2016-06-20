=======================
 Fleet Rental Document
=======================

Usage
=====

Use this module as base for other modules that work
with rental documents. For example, the fleet_rental_check_vehicle
inherits this module to add checklists on documents.
Some other modules may add something else.

* Open ``Fleet / Vehicles`` menu
* Under ``Rental Properties`` group for each vehicle define the following information:

 * Dayly rental price
 * Rate per extra km
 * Allowed kilometer per day

* Based on these values, Total Rental price will be automatically calculated in all documents.
