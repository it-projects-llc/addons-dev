====================
 POS Kitchen Screen
====================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way
* `Activate longpolling <https://odoo-development.readthedocs.io/en/latest/admin/longpolling.html>`__

Configuration
=============

POS Category Settings
---------------------

* Go to ``Point of Sale >> Configuration >> Pos Product Categories``
* Click on ``[Create]``
* Specify a **Name**
* Click ``[Create and edit ...]`` in the **Settings** field
* Specify a settings **Name**
* Specify the **States**
    - Click on ``[Create]``
    - Specify **Display Name**
    - Select **Type**
    - Specify a unique **Technical Name**
    - Specify the display order in **Sequence**
    - Check the box **Show State on Kitchen** if necessary
    - Check the box **Sound Signal** if need play sound after changing the state
    - Click on ``[Save & Close]``

* Specify the **Buttons**
    - Click on ``[Create]``
    - Specify **Button Label**
    - Specify **Button Background Color**
    - Specify **Button Name Color**
    - Check the box **Show the Button for Waiters** if necessary
    - Check the box **Show the Button in Kitchen** if necessary
    - Specify **Next State** to apply on clicking
    - Specify **Python Code** to check the button
    - Check the box **Close action** if necessary
    - Click on ``[Save & Close]``

* Click ``[Save]`` in the ``Settings``
* Click ``[Save]`` in the ``Pos Product Categories``

POS Settings for Waiters
------------------------

* Go to ``Point of Sale >> Configuration >> Point of Sale``
* Click on ``[Create]``
* Specify **Point of Sale Name**
* Specify **Specify Screen Type** like **Waiter**
* Specify the **Custom Buttons** for Orders

  * Click on ``[Create]``
  * Specify **Button Label**
  * Specify **Button Background Color**
  * Specify **Button Name Color**
  * Specify **Apply Tag**
        
     * Click on ``[Create]``
     * Specify **Display Name**
     * Specify a unique **Technical Name**
     * Specify **Tag Name Color**
     * Specify **Tag Background Color**
     * Specify **Priority**
     * Click on ``[Save]``

  * Specify **Remove Tag** if necessary
  * Click on ``[Save & Close]``

* Click ``[Save]``

POS Settings for Kitchen
------------------------

* Go to ``Point of Sale >> Configuration >> Point of Sale``
* Click on ``[Create]``
* Specify **Point of Sale Name**
* Specify **Specify Screen Type** like **Kitchen**
* Specify **Kitchen Display Product Categories**
* Check the box **Show Floors Plan** if pos_restaurant is installed

Usage
=====

* Open POS session for Waiters
* Add the Product which using Pos Category
* Click on State Button in the Orderline
* Click on Custom Button in the Order
* Open POS session for Kitchen
