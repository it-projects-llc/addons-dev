===============================
 Custom system for car renting
===============================


Adds roles:

    - Branch Officer
    - Vehicles Support Officer
    - Branch Employee
    - General Manager
    - Accountant
    - Payroll Officer


Adds branches in fleet module. Branches is stations between which cars are moved.

Adds partner personality info:

    - Date of birth (from partner_person module)
    - Nationality (from partner_person module)
    - Third Name
    - Family Name
    - ID Type
    - ID Number
    - Issuer
    - Date of Issue
    - License Type
    - License Number

Adds partner age restriction (must be 21 or elder) if he is customer (is customer field).

----------------
 Vehicle Rental
----------------

See ``fleet_rental_document`` module documentation.

Further information
-------------------

Demo: http://runbot.it-projects.info/runbot/34/addons-yelizariev-9.0-fleet_booking

HTML Description: https://apps.odoo.com/apps/modules/9.0/fleet_booking

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 9.0 d3dd4161ad0598ebaa659fbd083457c77aa9448d
