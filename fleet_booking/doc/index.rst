===============================
 Custom system for car renting
===============================


Current module overview
=======================

This module installing next build-in modules:hr, fleet, account.

* hr needed for branches inheritance and for basic hr stuff like payroll and so on.
* fleet in functional basis that going to be significantly extended and modified.
* account is for accounting purposes.
* partner_person is for partner(customer) fields extension.

==============
Specifications
==============

Ready functions
===============

Roles (access groups)
---------------------

Its made using build-in access groups odoo functionality.

* Open database as admin in debug mode (.../web?debug).
* Go to ``Settings / Users / Groups``. Here you will see new access groups with Fleet booking prefix.
* Go to ``Settings / Users / Users``. Here is new users, one for every group.
* You can login with any of that users to see database representation for each of them.

Branches
--------
Built with *hr.departments* inheritance.

* Login in system as General Manager (gm/gm) or Admin (admin/admin). *login/password*
* Go to fleet in main menu and next ``Configuration / Branches``. Create and edit branches here.

Customer features
-----------------

Create or edit customer:

* User with Branch Officer role enters in database.
* Open ``Contacts``.
* Open some contact.
* You will see customer form.
* Press ``[Edit]`` button.
* Enter **First Name** string.
* Enter **Second Name** string.
* Enter **Third Name** string.
* Enter **Family Name** string.
* Enter **Work Phone** string.
* Open ``Personal information`` tab.
    * Enter **Birthdate**.
    * If customer age less than 21 you will not be able to save contact and you will see according notification.
    * Enter **Nationality** string.
    * Select one from drop-down **ID Type** (National Id, Iqama, Passport).
    * Enter **ID Number** string.
    * Enter **Issuer** string.
    * Enter **Date of Issue**.
    * Select one from drop-down **License Type** (Private, General, International).
    * Enter **License Number** string.
* Open ``Contacts & Addresses`` tab.
    * Create new work contact (Contacts & Addresses section).
    * Create new home (Contacts & Addresses section) .
    * Create new emergency contact (Contacts & Addresses section).
* Open ``Internal notes`` tab.
    * Enter additional information here.
* Press save.


Vehicle workflow
================

Depreciation and enrollment
---------------------------

For depreciation purposes used build-in module ``Assets management``.

Firstly you need to enroll asset (vehicle):

* Go to ``Accounting / Purchases / Vendor bills``.
* Create new ``Vendor bill``.
* Select vendor (partner).
* Add product representing vehicle. Create it if  needed.
* Select ``Asset Category``. Edit it or create new category if needed.
    * Pay special attention to ``Journal Entries``. Make sure correct journal and accounts selected.
    * Configure ``Depreciation Method`` and ``Periodicity``.
* Fill other fields.
* Then press ``[Validate]`` and ``[Register payment]``.
* This document makes asset enrollment and money write-off accounting entries.
* Save and close document.

Secondly create asset model record:

* Go to ``Accounting / Adviser / Assets``.
* Create new asset.
    * Select ``Category``. Depreciation information will be auto-filled.
    * Select vehicle. Create it if needed. Just fill necessary fields.
    * Select invoice. Put here vendor bill you created earlier.
    * Enter ``Gross Value``. It is an amount to be depreciated.
    * Fill other fields.
    * Press ``[Confirm]`` and ``[Save]``.
    * Now you will see depreciation lines.
    * Press red circle on line you need to create accounting depreciation entries and press ``[Save]`` (it will become green).
    * In upper right corner ``Items`` count will increase. Press it to look up accounting entries.
    * Press ``[Modify Depreciation]`` to make some changes those like period extension or to select another strategy.

So vehicle is represented by three records: Product, Vehicle, Asset. Product and asset is needed only for accounting aims. Vehicle is main object you going to work with.

Register payments
-----------------

* Open vehicle.
* Go to ``Payments`` tab.
* Press ``[Add new item]``.
* Fill invoice with according data.

Remove Vehicle
--------------

* Go to ``Fleet``.
* Open ``Vehicles``.
* Open some vehicle.
* Press ``[Action]``.
* Press ``[Delete]``.

Maintenance
===========

Used build-in fleet.vehicle.log.services model.

Maintenance state stages: Draft -> Request -> Done -> Paid.

Configure record filter (to see what records needs your attention)
------------------------------------------------------------------

* Open menu.
* Depending on your role choose filter:
    * For vehicle support officer (show records with State = Request AND Service Type != In branch.)
    * For accountant (show records with State = Done)

First maintenance scheme (in branch)
------------------------------------

* Branch officer actions:
    * Opens vehicle to be maintenanced.
    * Push ``[Services]`` button. Opens ``Vehicles Services Logs`` menu.
    * Create new vehicle service document.
    * Select ``Service Type`` as ``In branch``. "B" section now is visible.
    * Enters odometer.
    * Puts ``Included Services`` lines.
    * Press ``[Submit]`` to submit order and to set status from ``Draft`` to ``Request``. Vehicle state becomes ``In shop``. It cant be rented now.
    * If for some reason rollback is required press ``[Cancel submit]``.
    * When all jobs finished press ``[Confirm]``. It automatically changes ``State`` from ``Request`` to ``Done``. Vehicle state becomes ``Active``.

* Vehicle support officer actions:
    * No actions required.

* Accountant actions:
    * Opens service document.
    * Creates invoices (``[New invoice]`` button). All created invoices visible in table.
    * When costs invoices paid press ``[Approve]``. It automatically changes ``State`` from ``Done`` to ``Paid``.
    * If for some reason rollback is required press ``[Cancel approve]``.

Second maintenance scheme (not in branch)
-----------------------------------------

* Branch officer actions:
    * Opens vehicle to be maintenanced.
    * Push ``[Services]`` button. Opens ``Vehicles Services Logs`` menu.
    * Create new vehicle service document.
    * Select ``Service Type`` that is not ``In branch``. "B" section now is hidden.
    * Press ``[Submit]`` to submit order and to set status from ``Draft`` to ``Request``.  Vehicle state becomes ``In shop``. It cant be rented now.
    * If for some reason rollback is required press ``[Cancel submit]``.

* Vehicle support officer actions:
    * Opens service document.
    * Enters new odometer.
    * Puts ``Included Services`` lines.
    * When jobs finished press ``[Confirm]``. It automatically changes ``State`` from ``Request`` to ``Done``. Vehicle state becomes ``Active``.
    * If for some reason rollback is required press ``[Cancel confirm]``.

* Accountant actions:
    * Opens service document.
    * Creates invoices (``[New invoice]`` button). All created invoices visible in table.
    * When costs invoices paid press ``[Approve]``. It automatically changes ``State`` from ``Done`` to ``Paid``.
    * If for some reason rollback is required press ``[Cancel approve]``.


Vehicle Transfer
================

New model fleet_booking.transfer.

Menu items:

* Open ``Fleet`` in main menu.
* Go to ``Transfers``. Here is ``Incoming`` and ``Outgoing`` menu sections.
* In ``Incoming`` user see only transfers were destination is his branch.
* In ``Outgoing`` user see only transfers were source is his branch.

Workflow is like that:

* Vehicles Support Officer creates transfer.
    * Select vehicle. Relational fields (Car Plate Number) auto-filled.
    * Select source branch.
    * Select destination branch.
    * Enter current odometer.
    * ``Delivery Status`` auto-sets to ``Not delivered``. Vehicles Support Officer cant edit it.
    * ``Receiving Status`` auto-sets to ``Not received``. Vehicles Support Officer cant edit it.
    * Presses ``[Submit]`` and ``[Save]`` buttons.
    * Vehicle branch auto-sets to ``In transfer``. Vehicle status auto-sets to ``In transfer``. Vehicle branch auto-sets to ``undefined``.

* When car is delivered
    * Vehicles Support Officer enters new odometer.
    * Source Branch Officer presses ``Confirm delivery``. Vehicle ``Delivery state`` changes to ``Delivered``.
    * Destination Branch Officer presses ``Confirm receiving``. Vehicle ``Receiving state`` changes to ``Received``.
        * Vehicle branch auto-sets equal to destination branch. Vehicle status auto-sets to ``Active``.
