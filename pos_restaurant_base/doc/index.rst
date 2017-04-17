==========================
 Hardware Network Printer
==========================

Technical module in POS.
The standard Printer class does not allow you to override the functions of this class.
This module copies the Printer class and sets the default printers and allows you to override the Printer class.

Usage
=====

Connection::

    var Printer = require('pos_restaurant.base');

Using::

    Printer.include({
        print: function(receipt){
            // your code
            // call super method this._super(receipt);
        }
