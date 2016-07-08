================================
 Vendor bills for vehicle costs
================================

User manual
===========

Preparation
-----------

* Enter in debug mode.
 * `Enable technical features <https://odoo-development.readthedocs.io/en/latest/odoo/usage/technical-features.html>`_
* Go to ``Fleet / Configuration / Service Types``.
* Select according product for every service type you need.


Bills creation
--------------

* Go to ``Fleet / Vehicles`` and open some vehicle.
* Press ``[Contracts]``.
* Create new contract.
    * Fill all required fields. Especially pay attention to:
        * ``Recurring Cost Amount`` - amount, to be periodically billed.
        * ``Vendor`` - used in bill.
        * ``Included Services`` - service lines, that have product specified, to be placed in bills.
        * Save document.
* Wait till database automatically creates costs and bills documents or you may manually make it happened:
    * Go to ``Settings / Automation / Scheduled Actions``.
    * Open ``Generation of contracts costs based on the costs frequency``.
    * Press ``[Run Manually]``.
* Go to that vehicle ``[Contracts]`` again and open contract you have created.
* Open ``Generated Recurring Costs`` tab. Here you can see generated costs. Records created for dates form ``Contract Start Date`` to actual time with periodical that you set.
* Open ``Generated Vendor Bills`` tab to look up created bills.

Consider that bills are created but not validated.
Assumes that company accountant will validate and register payment manually when the time comes.
