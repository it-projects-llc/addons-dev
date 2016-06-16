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

Not ready functions
===================

Below stuff planned but not completed yet. It partially finished or developing now.

Customer features
-----------------

2. Customer Membership Management form
     Можно закинуть например в Sales/Configuration
     Поля
      - Customer Membership Or ID Number
      - Customer name - подгружается автоматически исходя из Customer Membership Or ID Number
      - Membership Type - подгружается автоматически исходя из Customer Membership Or ID Number
      - Action Type - выпадалка с 2мя значениями: Demote, Block
           * если выбрано Demote появляется
                       выпадалка Choose new membership с 2мя значениями: silver, bronze
                       поле Demoting reason
           * если выбрано Block появляется

                    поле Blocking reason
    Замечание: если у клиента Membership Type = 'Bronze', то понижать его уже некуда. В этом случае можно например при выборе Demote выдавать предупреждение вида:
        "Membership Type cannot be demoted"  (Membership Type не может быть понижен) или "Customer membership cannot be demoted"

Add (Edit) Vehicle
------------------

* Go to Fleet.
* Open Vehicles.
* Open some vehicle.
* Press Edit button.
    * Select model or create new one. Enter ``Model name`` and ``Make (brand)``.
    * Select color from drop-down. // add
    * Enter Model Year. //rename Acquisition Date
    * Car Plate Number // rename License Plate
    * Car chassis number
    * Go to Costs.
        * Create new cost with **Daily Rate** type. Enter in **Total price** daily rental price. // add xml rec
        * Create new cost with **Rate per extra km** type. Enter in **Total price** rate per extra km. // add xml rec
    * Enter allowed kilometer per day // add
    * Enter Vehicle registration expiry date // add
    * Enter Insurance expiry date // add
    * Enter Lease Installments dates // add Table ( model) . даты платежей за прокат
    * Enter Insurance Installments dates // add Table ( model) . даты платежей за страховку
    * Enter Odometer
    *  Purchase Price // rename car value
    *  Paid Amount // add
    *  Remaining Amount  // add
    *  Asset Account  // add
    *  Paid Amount Account  // add
    *  Remaining Amount Account  // add
    *  Vehicle Depreciation - амортизация ТС - в табличном виде (возможно one2many)
    *  Depreciation Expense Account - счет для расходов на амортизацию (Many2one)
    *  Accumulated Depreciation Account - счет для накопленной амортизации  (Many2one)
    *  Next Maintenance Date - дата следующего сервисного обслуживания (тип Date)
    *  Press save.

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
