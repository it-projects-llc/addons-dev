Hours-based service sales
=========================

The modules adds extra feature to built-in *Sales/Contracts*:
* *Prepaid Service Units* is computed based on paid invoices with products marked as *Timesheets on contracts*.
* Contract Reports - report on paid, used, unused hours for specific period
* Invoice Extra Timesheets (Timesheet minus prepaid service, minus invoiced timesheet)


Usage
-----

* Grant access *Manage Multiple Units of Measure* to your user (in odoo 8.0 you have to grant *Technical features* first and then refresh user form)
* Create product.template:

  * set *Track service* field to *Timesheets on contracts*
  * *Unit of Measure* is *Hour(s)* by default, but you can change to  value (days, weeks etc.)
  * On *Variants* tab create attribute with *Technical Name* equal to *TIMESHEET* and add Attribue Values with some *Technical Values*, e.g. 20, 40, 80

* Create contract on *Sales \ Contract*:

  * switch on checkboxs:

    * *Timesheets*
    * Invoicing: *Fixed Price* (built-in)
    * Invoicing: *On Extra Timesheets* (new)

  * click on *Sale Orders*  link, create sale.order with product above. Confirm sale, Create invoice, Validate invoice, Register payment

* Timesheets

  * open contract

    * *Prepaid Service Units* has to be changed to corresponded value (new)
    * Create Timesheets

      * Use (create) product with following values:
        * UoM: *Hour(s)*.

    * Units consumed is changed (built-in feature)

* Recurring invoices

  * open contract

    * switch *Generate recurring invoices automatically* on

      * Date of Next Invoice is some passed date (for testing only)
      * Invoice lines

        * One of TIMESHEET Product

  * Open *Settings\Technical\Automation\Scheduled Actions*:

    * *Generate Recurring Invoices from Contracts*: change *Next Execution Date* to Now.
    * wait a minute
    * Check new invoices in *Accounting/Customer Invoices* - they have a draft state and have to be validated and sent manually

      * Validate and register payment for one of invoices

  * open contract

    * prepaid Service units is updated

* Recurring Reports

  * open contract

    * switch *Generate recurring reports automatically* on

      * Date of Next Report is some passed date (for testing only)

  * Open *Settings\Technical\Automation\Scheduled Actions*:

    * *Generate Recurring Reports from Contracts*: change *Next Execution Date* to Now.
    * wait a minute
    * Check new invoices in *Sales/Contract Reports* - they have a draft state and have to be validated and sent manually

      * sent report to customer
  
* Recurring invoices on Extra Timesheets

  * open contract

    * switch *Generate recurring invoices automatically  (on extra timehsheets)* on

      * Date of Next Invoice is some passed date (for testing only)
      * *Extra Timesheet Product* - any service product.

    * Create timesheets as described above in order to exceed prepaid hours
  * Open *Settings\Technical\Automation\Scheduled Actions*:

    * *Generate Recurring Invoices from Contracts (on extra timesheets)*: change *Next Execution Date* to Now.
    * wait a minute
    * Check new invoices in *Accounting/Customer Invoices* - they have a draft state and have to be validated and sent manually

      * Validate and register payment for one of invoices

  * open contract

    * prepaid Service units is updated
      

Further information
-------------------

HTML Description: https://apps.odoo.com/apps/modules/8.0/sale_contract_hours

Tested on Odoo 8.0 a40d48378d22309e53e6d38000d543de1d2f7a78
