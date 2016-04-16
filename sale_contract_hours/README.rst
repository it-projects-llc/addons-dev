Hours-based service sales
=========================

The modules adds extra feature to built-in *Sales/Contracts*:

* *Prepaid Service Units* is computed based on paid invoices with products with *Prepaid Service Units* attributes.
* Extended Invoice
  * used as periodic report on work done:
    * Period start
    * Period end
    * Prepaid hours before period
    * Used hours on period
    * Prepaid hours after period
  * Invoice Extra Timesheets (Timesheet minus prepaid service, minus invoiced timesheet)
  * Change meaning of *Invoicable* field (e.g. *Yes (100%)*). It's used to change quantity of hours, while out-of-box it means discount (i.e. change price only). 
* Smart button *Unpaid Invoices* (amount)


Usage
-----

* Grant access to your user (in odoo 8.0 you have to grant *Technical features* first and then refresh user form):

  * *Manage Multiple Units of Measure*
  * *Analytic Accounting*
  * *Analytic Accounting for Sales*
  * *Accounting & Finance: Financial Manager*

* Create product.template:

  * *Unit of Measure* is *Hour(s)* by default, but you can change to  value (days, weeks etc.)
  * On *Variants* tab create attribute with *Technical Name* equal to *Prepaid Service Units*

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

    * Units consumed is changed (built-in)

* Recurring invoices (built-in)

  * open contract

    * switch *Generate recurring invoices automatically* on

      * Date of Next Invoice is some passed date (for testing only)
      * Invoice lines

        * One of *Prepaid Service Units* Product
        * Quantity

  * Open *Settings\Technical\Automation\Scheduled Actions*:

    * *Generate Recurring Invoices from Contracts*: change *Next Execution Date* to Now.
    * wait a minute
    * Check new invoices in *Accounting/Customer Invoices* - they have a draft state and have to be validated and sent manually

      * Validate and register payment for one of invoices

  * open contract

    * prepaid Service units is updated (new)

* Reports

  * Before generating reports, there must be confirmed timesheets. It can be done via *Human Resources/Time Tracking*

    * Employee create timesheet via *My current timesheet* menu
    * Manager validate timesheets via *Timesheets to Validate* menu

  * open Sales/Contracts menu

    * select contracts
    * click Action -> Generate reports

      * Select start and end date
      * click Apply

  * Check new account.invoice records in *Invoicing/Invoices* - they have a draft state and have to be validated and sent manually

    * invoice has:

      * lines with prepaid timesheets (price = 0)
      * lines on extra timesheets (price > 0)

* Analytic account

  * open *Invoicing/Analytic Journal Items*

    * Apply *Group by "Analytic Account"*
    * then Apply *Group by "Journal"*
    * Column *Quantity* is used to count service

      * In Sale journal - invoiced hours
      * In Timesheet journal - used hours


Further information
-------------------

HTML Description: https://apps.odoo.com/apps/modules/8.0/sale_contract_hours

Tested on Odoo 8.0 a40d48378d22309e53e6d38000d543de1d2f7a78
