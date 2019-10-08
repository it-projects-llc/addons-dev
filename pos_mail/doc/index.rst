======================
 POS Receipts by mail
======================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Open menu ``[[ Point of Sale ]] >> Configuration >> Settings``
* Scroll down to ``[POS Mail Message]``
* Click on icon on right from ``Select Box``
* Fill the required fields
* For `properly-handled` text: in html-editor enter ``'Code View'``-mode by clicking ``"</>"``-icon

Template example:

    ---

    <p>Dear, ${partner.name}</p>

    <p>Thanks for purchasing in our shop</p>

    <p>Your order is: ${order.pos_reference}</p>

    <p>Best wishes.</p>


Will be converted to

    ---

    <p>Dear, Bob</p>

    <p>Thanks for purchasing in our shop</p>

    <p>Your order is: ${order.pos_reference}</p>

    <p>Best wishes.</p>


Usage
=====

* Open POS session
* Choose customer with email
* Create order and validate it
* Click ``[Mail Receipt]``
*RESULT: A letter is sending to the User with the receipt in the attachment, and with a template in the message body.
