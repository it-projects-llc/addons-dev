===============================
 Custom system for car renting
===============================

==============
Specifications
==============


Roles (access groups)
---------------------

It is made using build-in access groups odoo functionality.

* Open database as admin in debug mode (.../web?debug).
* Go to ``Settings / Users / Groups``. Here you will see new access groups with *Fleet booking* prefix.
Every role has specific use with appropriated to it restrictions and access permissions.

Main roles is:
    * General Manager
    * Branch Officer
    * Vehicles Support Officer
    * Branch Employee
    * Accountant
    * Payroll Officer

These roles will be often referred further in this documentation.

* Go to ``Settings / Users / Users``. Here you will see demo users, one for every group, but only if you created database with *load demonstration data*.
* You can login with any of that users to see database representation for each of them.

Branches
--------

* Login in system as General Manager (gm/gm) or Admin (admin/admin). *login/password*
* Go to fleet in main menu and next ``Configuration / Branches``. Create and edit branches here.
* Go to ``Settings / Users / Users``. Set corresponding branch to every user you need. It will cause branch limitations for some data in system for that user.
* Also you may set according branch for vehicles.

Customer features
-----------------

Create or edit customer (as Branch Officer):

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

All actions, regarding assets and depreciation, supposed in duty of Accountant.

Firstly you need to enroll asset (vehicle):

* Go to ``Accounting / Purchases / Vendor bills``.
* Create new ``Vendor bill``.
* Select vendor (partner).
* Add product representing vehicle. Create it if needed.
* Select ``Asset Category``. Edit it or create new category if needed.
    * Pay special attention to ``Journal Entries``. Make sure correct journal and accounts selected.
    * Configure ``Depreciation Method`` and ``Periodicity``.
* Fill other fields.
* Then press ``[Validate]`` and ``[Register payment]``.
* This document creates asset record and makes asset enrollment and money write-off accounting entries (on payment register).
* Save and close document.

Secondly manage created asset:

* Go to ``Accounting / Adviser / Assets``.
* Here you will see automatically created asset for product (vehicle) you just enrolled. Open it.
    * Select vehicle. Create it if needed. Just fill necessary fields.
    * Press ``[Confirm]`` and ``[Save]``.
    * Press red circle on depreciation line you need (in ``Residual`` column) to create accounting depreciation entries and press ``[Save]`` (it will become green).
    * In upper right corner ``Items`` count will increase. Press it to look up accounting entries.
    * Press ``[Modify Depreciation]`` to make some changes those like period extension or to select another strategy.

So vehicle is represented by three records: Product, Vehicle, Asset. Product and asset is needed only for accounting aims. Vehicle is main object you going to work with.

Remove Vehicle
--------------

* Go to ``Fleet``.
* Open ``Vehicles``.
* Open some vehicle.
* Press ``[Action]``.
* Press ``[Delete]``.


Maintenance
===========

Document ``Vehicles Services Logs`` used to manage vehicles maintenance.

Maintenance state stages: Draft -> Request -> Done -> Paid.

First maintenance scheme (in branch)
------------------------------------

* Branch officer actions:
    * Open vehicle to be maintenanced.
    * Push ``[Services]`` button. Open ``Vehicles Services Logs`` menu.
    * Create new vehicle service document.
    * Select ``Service Type`` as ``In branch``. "B" section now is visible.
    * Enter odometer.
    * Put ``Included Services`` lines.
    * Press ``[Submit]`` to submit order and to set status from ``Draft`` to ``Request``. Vehicle state becomes ``In shop``. It cant be rented now.
    * If for some reason rollback is required then press ``[Cancel submit]``.
    * Press ``[Confirm]`` when all jobs is finished. It automatically changes document state from ``Request`` to ``Done``. Vehicle state becomes ``Active``.

* Vehicle support officer actions:
    * No actions required.

* Accountant actions:
    * Open service document.
    * Create invoices (``[New invoice]`` button). All created invoices visible in ``Invoices`` table.
    * Press ``[Approve]`` when costs invoices paid. It automatically changes ``State`` from ``Done`` to ``Paid``.
    * You can ``[Cancel approve]`` if you need.

Second maintenance scheme (not in branch)
-----------------------------------------

* Branch officer actions:
    * Open vehicle to be maintenanced.
    * Push ``[Services]`` button. Open ``Vehicles Services Logs`` menu.
    * Create new vehicle service document.
    * Select ``Service Type`` that is not ``In branch``. That causes "B" section becomes hidden.
    * Press ``[Submit]`` to submit order and to set document status from ``Draft`` to ``Request``.  Vehicle state changes to ``In shop``. It cant be rented now.
    * You can ``[Cancel submit]`` if you need.

* Vehicle support officer actions:
    * Open service document.
    * Enter new odometer.
    * Put ``Included Services`` lines.
    * Press ``[Confirm]`` when all jobs is finished. That automatically changes document state from ``Request`` to ``Done``. Vehicle state becomes ``Active``.
    * You can ``[Cancel confirm]`` if you need.

* Accountant actions:
    * Open service document.
    * Create invoices (``[New invoice]`` button). All created invoices visible in ``Invoices`` table.
    * Press ``[Approve]`` when costs invoices paid. It automatically changes document state from ``Done`` to ``Paid``.
    * You can ``[Cancel approve]`` if you need.


Vehicle Transfer
================

Document ``Transfer`` used to manage locations (branches) of vehicles.

Menu items:

* Open ``Fleet`` in main menu.
* Go to ``Transfers``. Here is ``Incoming``, ``Outgoing`` and ``All transfers`` menu sections.
* In ``Incoming`` user see only those transfers, where destination coincides with his branch.
* In ``Outgoing`` user see only those transfers, where source coincides with his branch.

Workflow is like that:

* Vehicles Support Officer creates transfer.
    * Select vehicle. Relational fields (Car Plate Number) auto-filled.
    * Select source branch.
    * Select destination branch.
    * Enter current odometer.
    * Document ``Delivery Status`` auto-sets to ``Not delivered``. Vehicles Support Officer cant edit it.
    * Document ``Receiving Status`` auto-sets to ``Not received``. Vehicles Support Officer cant edit it.
    * Press ``[Submit]`` and ``[Save]`` buttons.
    * Document state auto-sets to ``Transfer``. Vehicle status auto-sets to ``In transfer``. Vehicle branch auto-sets to ``undefined``.

* When car is delivered
    * Vehicles Support Officer enters new odometer.
    * Source Branch Officer presses ``Confirm delivery``. Document ``Delivery state`` changes to ``Delivered``.
    * Destination Branch Officer presses ``Confirm receiving``. Document ``Receiving state`` changes to ``Received``.
        * Vehicle branch auto-sets equal to document destination branch. Vehicle status auto-sets to ``Active``.
