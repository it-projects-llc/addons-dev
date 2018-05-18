.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

=========================
 Income-Expense Analysis
=========================

Split expenses in quants and distribute them among income. This allows to know
not only profitablity of the projects, but also structure of expenses in the
incomes.

Imagine that incomes are big containers and each expense is splitted into small boxes
(*quants*). Now, depending on relation between expenses and incomes small boxes
are distributed in containers.

* If containers has some free space after distribution -- that income (related to some project) is profitable.
* If small boxes are not fit to related containers, then those expenses are not covered by corresponding incomes.


Built-in model ``account.analytic.line`` has additional fields:

* ``line_ids`` specifies weighted link to analytic records of opposite
  type (i.e. an expense has links to incomes only and vice versa)
* ``date_start``, ``date_end`` -- interval of income/expense accumulation (e.g. 1 month for montly rent fee)


How *quants* are distributed:

* Beggining from the oldest expenses, distirbute quants to corresponding
  containers proportionally to link weight
* At next stage, we are trying to destribute quants to containers that belong to
  quants' interval. Quants are distributed proportionally to size of found
  contaiers
* At the last stage, we are trying to find cointainers with the closest date

Roadmap
=======

* ``hr_timesheet`` dependency can be taken out to new module ``account_analytic_quants_hr_timesheet``

Credits
=======

Contributors
------------
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support you are kindly requested to purchase the module at `odoo apps store <https://apps.odoo.com/apps/modules/10.0/account_analytic_quant/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/misc-addons/10.0

HTML Description: https://apps.odoo.com/apps/modules/10.0/account_analytic_quant/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Notifications on updates: `via Atom <https://github.com/it-projects-llc/misc-addons/commits/10.0/account_analytic_quant.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/misc-addons/commits/10.0/account_analytic_quant.atom>`_

Tested on Odoo 10.0 475027b9889c0701f8fe5e0373a40663f6a831e1
