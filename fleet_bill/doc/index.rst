================================
 Vendor bills for vehicle costs
================================

User manual
===========

Preparation
-----------

* Enter in debug mode.
* Go to ``Fleet / Configuration / Service Types``.
* Select according product for every service type you need.


Bills creating
--------------

* Go to ``Fleet / Vehicles`` and open some vehicle.
* Press ``[Contracts]``.
* Create new contract.
    * Fill all required fields. Especially pay attention to:
        * ``Recurring Cost Amount`` - amount to be periodically billed.
        * ``Vendor`` - on which name bills are.
        * ``Included Services`` - product lines to be placed in bills.
        * Save document.
* Wait till database automatically create costs and bills documents or manually force it happened:
    * Go to ``Settings / Automation / Scheduled Actions``.
    * Open ``Generation of contracts costs based on the costs frequency``.
    * Press ``[Run Manually]``.
* Go to that vehicle ``[Contracts]`` again and open contract you have created.
* Open ``Generated Recurring Costs`` tab. Here you can see generated for costs. Records created for dates form ``Contract Start Date`` to actual time with periodical that you pointed.
* Open ``Generated Vendor Bills`` tab to look up created bills.

Consider that bills are created but not validated.
Assumes that company accountant will validate and register payment manually when the time comes.