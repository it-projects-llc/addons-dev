==========================
 Hardware Network Printer
==========================

Installation
============

* Comment in hw_escpos/controllers/main.py 354th line (replace driver.push_task('printstatus') to # driver.push_task('printstatus')), This module should be installed to POS Box
* Install the hw_printer_network module in the POS Box
* Install the pos_printer_network module in the Odoo

Usage
=====

* Open the POS
* Add new product in order
* Click ``[Order]``
