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

Customer membership:

* TODO

Not ready functions
===================

Below stuff planned but not completed yet. It partially finished or developing now.

Vehicle workflow
----------------

For depreciation purposes used build-in module ``Assets management``.

Firstly you need to enroll asset (vehicle):

* Go to ``Accounting \ Purchases \ Vendor bills``.
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

* Go to ``Accounting \ Adviser \ Assets``.
* Create new asset.
    * Select ``Category``. Depreciation information will be auto-filled.
    * Select vehicle. Create it if needed.
    * Select invoice. Put here vendor bill you created earlier.
    * Enter ``Gross Value``. It is an amount to be depreciated.
    * Fill other fields.
    * Press ``[Confirm]`` and ``[Save]``.
    * Now you will see depreciation lines.
    * Press red circle on line you need to create accounting depreciation entries and press ``[Save]`` (it will become green).
    * In upper right corner ``Items`` count will increase. Press it to look up accounting entries.
    * Press ``[Modify Depreciation]`` to make some changes those like period extension or to select another strategy.

So vehicle is represented by three records: Product, Vehicle, Asset. Product and asset is needed only for accounting aims. Vehicle is main object you going to work with.


Remove Vehicle
--------------

* Go to Fleet.
* Open Vehicles.
* Open some vehicle.
* Press Edit button.
    * PressRemove button.
    * Fill popped up form. If it sold put also Selling price.


Vehicle Contracts
-----------------

To create new rent document:
 * from ``Fleet Rental / Rent Quotations`` click ``[Create]``
 Fill the opened form with client and car information.
 To be able to confirm the document you should also fill the ``Exit Date`` and ``Return Date``
 along with a payment information. When it is done click ``[Confirm Rental]`` button.
 If don't have payment information at this point you can still book the rent without confirmation.
 The ``Exit Date`` and ``Return Date`` should be filled. Then click ``[Book only]`` button.

To create extended rent:
 * from ``Fleet Rental / Confirmed Rents`` select rent that you want to extended.
 * Click ``[Extend]`` button to create new extended rent.

To create return document:
 * from ``Fleet Rental / Confirmed Rents`` select rent that should be returned.
 * Click ``Return`` button to create new return document.

To confirm return document:
 * from ``Fleet Rental / Draft Return Contracts`` open the document to confirm.
 * Depending on current payment state you can confirm as open or confirm as closed.
 * If the car is returned but client hasn't fully paid for the rent then click ``[Return Car and Keep Contract Open]`` button.
 * If the car is returned and client has fully paid for the rent then click ``[Confirm Return]`` button.




* Go to Fleet.
* You will see *Movements* section in left panel menu. This section has 3 rows.  Rent, Receive, Extending Contract, Return Vehicle. Actually its just a different representation fo same model with contract type binding.
* Press Rent.
* Select customer (drop-down). After that next fields will be filled automatically (in customer block):
    * Customer name
    * Customer membership number
    * Membership Type
* Select Vehicle (drop-down). After that next fields will be filled automatically  (in vehicle block):
    * Vehicle Model
    * Car Plate
    * Color
    * Daily rental price
    * Allowed kilometer per day
    * Rate per extra km
    * Odometer
* Check Vehicle status. Mark some details checkboxes if needed. In future car parts painting will be.
    * tires - шины
    * spare tire - запасное колесо
    * oil - масло
    * floor - дно машины
    * jack - домкрат
    * horn - звуковой сигнал
    * triangle - знак аварийной остановки
    * wrench - гаечный ключ
    * hub cups - колпаки ступицы
    * antenna - антенна
    * radio - радио
    * glass - автомобильное стекло
* Select additional driver. After that next fields will be filled automatically (in additional driver block):     
     * License Number - номер водительского удостоверения
     * Issuer -  кем выдан
     * License Expiry Date - дата истечения вод. удостоверения  (Date)
     * License Type - выпадалка с 3мя значениями: Private, General, International  (Selection)
* Agreement expiry date - дата истечения договора (Date)
* Exit Date и Exit Time - дата и время передачи клиенту ТС (можно Datetime)
* Return Date - дата возврата ТС
* Payment method - способ оплаты - выпадалка с 3мя значениями: Cash, Span, Visa or Master Card если выбрано Visa or Master Card, то должны появляться поля:
    * Name On Card - имя владельца карты
    * Card Number - номер карты
    * Card Expiry Date - дата истечения действия карты
* Amount - общая стоимость аренды без скидки
* Discount - скидка в процентах
* Total - стоимость с учетом скидки, явно не указано, что должно вычисляться автоматически однако думаю лучше сделать auto calculated используя формулу: Total = Amount - Amount * Discount / 100. Соответственно если скидки нет, то в Total записывается значение Amount.
* Deposit - сумма предоплаты
* Remaining amount - оставшаяся сумма оплаты, вычисляется автоматически по формуле: Remaining amount = Total - Deposit.
* Go to Fleet.
* You will see Return Vehicle in *Movements* section.
* If you are Branch Officer you will see next fields:
    * Customer
    * Interactive Car -> Vehicle
    * Damage Cost - стоимость повреждений ТС
    * Way to cover damage costs - способ возмещения - выпадалка с 3мя значениями:
        * Direct from customer
        * By customer’s insurance
        * lessor's insurance
    * Extra charge - дополнительная плата
    * Return Date и Return Time - дата и время возврата ТС
* If you are Branch Employee you will see next fields:
    * Odometer in receiving - километраж при получении ТС
    * Vehicle Body - выпадалка с 2мя значениями: In good condition, Not in good condition
    * Inside Vehicle - выпадалка с 2мя значениями: In good condition, Not in good condition
    * Damage Type - тип повреждения
    * Notes - дополнительные заметки
* Agreement expiry date, Exit Date, Exit Time
* Exit Vehicle status checkbox line (automatically taken from rental document)
* Return Vehicle status checkbox line
* Exceeded kilometers/hours - превышенное кол-во км и часов - вычисляется автоматически
    Exceeded kilometers = Odometer in receiving - Odometer (берем из карточки ТС) - Rented Period * Allowed kilometer per day (берем из карточки ТС),
    где Rented Period = Return Date - Exit Date
    Exceeded hours = Return date and time – Exit date and time – Allowed hours to be late (о последнем параметре ни в какой из форм не упоминается, поэтому будем уточнять)
* Total - вычисляется автоматически:
    Total = Total (из контракта Rent) + Exceeded kilometers cost + Exceeded hours cost + Extra charge,
    где Exceeded kilometers cost = Rate per extra km (берем из карточки ТС) * Exceeded kilometers,
    Exceeded hours cost = Rate per extra hour (по этому параметру тоже нет инфо в документе, будем уточниять) * Exceeded hours
* Deposit - подтягивается автоматически из контракта Rent
* Remaining amount - вычисляется автоматически: Remaining amount = Deposit - Total.


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
    * When all jobs finished press ``[Confirm]``. It automatically changes ``State`` from ``Request`` to ``Done``, saves and closes document. Vehicle state becomes ``Active``.

* Vehicle support officer actions:
    * No actions required.

* Accountant actions:
    * Opens service document.
    * Creates invoices (``[New invoice]`` button). All created invoices visible in table.
    * When costs invoices paid press ``[Approve]``. It automatically changes ``State`` from ``Done`` to ``Paid``, saves and closes document.

Second maintenance scheme (not in branch)
-----------------------------------------

* Branch officer actions:
    * Opens vehicle to be maintenanced.
    * Push ``[Services]`` button. Opens ``Vehicles Services Logs`` menu.
    * Create new vehicle service document.
    * Select ``Service Type`` that is not ``In branch``. "B" section now is hidden.
    * Press ``[Submit]`` to submit order and to set status from ``Draft`` to ``Request``.  Vehicle state becomes ``In shop``. It cant be rented now.

* Vehicle support officer actions:
    * Opens service document.
    * Enters new odometer.
    * Puts ``Included Services`` lines.
    * When jobs finished press ``[Confirm]``. It automatically changes ``State`` from ``Request`` to ``Done``, saves and closes document. Vehicle state becomes ``Active``.

* Accountant actions:
    * Opens service document.
    * Creates invoices (``[New invoice]`` button). All created invoices visible in table.
    * When costs invoices paid press ``[Approve]``. It automatically changes ``State`` from ``Done`` to ``Paid``, saves and closes document.

Vehicle Transfer
================

New model fleet_booking.transfer.

Menu items:

* Open ``Fleet`` in main menu.
* Go to ``Transfers``. Here is ``Incoming`` and ``Outgoing`` menu sections.
* Тут надо сказать про то что в Incoming по умолчанию видны только входящие для бранча активного эмплоера. Я не знаю как это делать то ли фильтрами то ли что.
* Аналогично для  Outgoing

Workflow is like that:

* Vehicles Support Officer creates transfer.
    * Select vehicle. Relational fields (Car Plate Number) auto-filled.
    * Select source branch.
    * Select destination branch.
    * Enter current odometer.
    * ``Delivery Status`` auto-sets to ``Not delivered``. Vehicles Support Officer cant edit it.
    * ``Receiving Status`` auto-sets to ``Not received``. Vehicles Support Officer cant edit it.
    * Presses ``[Save]`` button.
    * Vehicle branch auto-sets to ``In transfer``. Vehicle status auto-sets to ``In transfer``.

* When car is delivered
    * Vehicles Support Officer enters new odometer.
    * Source Branch Officer sets ``Delivery Status`` to ``Delivered``.
    * Destination Branch Officer sets ``Receiving Status`` to ``Delivered``.
    * Vehicle branch auto-sets equal to destination branch. Vehicle status auto-sets to ``Active``.


