===============================
 Custom system for car renting
===============================

It uses (inherits) HR and Fleet odoo 9 genuine modules.

How to check it:

* Install module
* Go to fleet in main menu
* Go to department in Configuration section

Updates is here: https://github.com/yelizariev/addons-dev/pull/57


==============
Specifications
==============

Customer features
-----------------

1 Stage::

   * Create or edit customer
   * User with Branch Officer role enters in database.
   * Open Contacts.
   * Open some contact.
   * You will see customer form.
   * Press edit button.
   * Enter Date of Birth.
   * If customer age less than 21 you will not be able to save contact and you will see according notification.
   * Enter Nationality string.
   * Select one from dropdown ID Type (National Id, Iqama, Passport).
   * Enter ID Number string.
   * Enter Issuer string.
   * Enter Date of Issue.
   * Select one from dropdown License Type (Privatem General, International).
   * Enter License Number string.
   * Enter Work Phone Number string.
   * Enter Customer Home Address string.
   * Enter Customer Work Address string.
   * Create new contact (Contacts & Addresses section) for emergency cases.
   * Enter additional information in Internal Notes section.
   * Press save.


Add (Edit), Remove Vehicle
--------------------------

1 Stage::

   * Go to Fleet.
   * Open Vehicles.
   * Open some vehicle.
   * Press Edit button.
   * Fill required fields.
   * Vehicle Model -> Model
   * Vehicle Brand -> Make (open form Create: Model)
   * Color -> Dropdown selection
   * Car Plate Number -> License Plate
   * Car chassis number -> Chassis number
   * Daily rental price (Daily Rate)
   * Rate per extra km
   * Allowed kilometer per day
   * Vehicle registration expiry date
   * Insurance expiry date
   * Lease Installments dates Table
   * Insurance Installments dates Table
   * Odometer -> Last Odometer
   
2 Stage::

   * Go to Fleet.
   * Open Vehicles.
   * Open some vehicle.
   * Press Edit button.
   * PressRemove button.
   * Fill poped up form. If it sold put also Selling price.
