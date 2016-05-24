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


Vehicle Contracts
-----------------

Stage 1::

    * Go to Fleet.
    * You will see *Movements* section in left panel menu. This section has 3 rows.  Rent, Receive, Extending Contract, Return Vehicle. Actually its just a different representation fo same model with contract type binding.
    * Press Rent.
    * Select customer (dropdown). After that next fields will be filled automatically (in customer block):
         * Customer name
         * Customer membership number
         * Membership Type
    * Select Vehicle (dropdown). After that next fields will be filled automatically  (in vehicle block):
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
    * Payment method - способ оплаты - выпадалка с 3мя значениями: Cash, Span, Visa or Master Card
             если выбрано Visa or Master Card, то должны появляться поля:
        * * Name On Card - имя владельца карты
                 * Card Number - номер карты
                 * Card Expiry Date - дата истечения действия карты
    * Amount - общая стоимость аренды без скидки
    * Discount - скидка в процентах
    * Total - стоимость с учетом скидки, явно не указано, что должно вычисляться автоматически однако думаю лучше сделать auto calculated используя формулу:
            Total = Amount - Amount * Discount / 100
        Соответственно если скидки нет, то в Total записывается значение Amount.
    * Deposit - сумма предоплаты
    * Remaining amount - оставшаяся сумма оплаты, вычисляется автоматически по формуле:
            Remaining amount = Total - Deposit

