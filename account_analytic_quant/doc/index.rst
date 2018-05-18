=========================
 Income-Expense Analysis
=========================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

+* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* If you don't have access level **Accounting & Finance:**	*Adviser*, set it in ``[[ Settings ]] >> Users >> Users``.
* Open menu ``[[ Accounting ]] >> Adviser >> Analytic Entries``.
* For existing records Specify values for following fields:

  * **Linked Records** -- related analytic records of opposite type. To set
    Weight of the links, save the record first, then click edit again -- you can
    set the weight and *Weights of the Links* tab
  * **Date Start**, **Date End** -- interval of income/expense accumulation.


* Open Wizard via menu ``[[ Accounting ]] >> Adviser >> Generate Analytic Quants``

  * Set **Starting Date** filter and **Quant Size**
  * Click ``[Generate]``

* Open menu ``[[ Accounting ]] >> Adviser >> Analytic Quants``
* Reload web page to apply filter for latest Generation

* RESULT: You can analyze Expenses / Incomes
