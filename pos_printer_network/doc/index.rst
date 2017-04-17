=====================
 POS Network Printer
=====================

Installation
============

* Install the hw_printer_network module in the POS Box
* Install the pos_printer_network module in the Odoo

Configuration
=============

* go to ``Point of Sale >> Order Printers``

  * Click on ``[Create]``
  * Specify the name of the new printer in the Printer Name field
  * Specify the proxy server IP address of the Network printer
  * Specify the value of Network Printer True if this printer is a network printer
  * Specify Printed Product Categories
  * Click ``[Save]``

* go to ``Point of Sale >> Point of Sale``

  * Open the POS in Configuration
  * Click on ``[Edit]``
  * In Order Printers Add an item (New printer)
  * Click ``[Save]``
  * Specify the proxy server IP address of the POS Box
  * Specify the proxy server IP address of the Network printer for receipt printer

Usage
=====

* Open the POS
* Add new product in order
* Click ``[Order]``
