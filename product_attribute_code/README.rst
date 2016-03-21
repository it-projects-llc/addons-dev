Technical codes and values on product attributes
================================================

Module allows attach codes on attributes to use it in other modules.

Example
-------

If product is a Hosting, then attribute codes and values could be:

* product.attribute: code=RAM

  * product.attribute.value: code_value="100MB"
  * product.attribute.value: code_value="500MB"

* product.attribute: code=OS

  * product.attribute.value: code_value="Ubuntu 12.04"
  * product.attribute.value: code_value="Ubuntu 14.04"

Then custom module could handle such attributes on sales and prepare corresponded server.

Usage
-----

* Open Product (e.g. via *Sales/Products/*)

  * *Variants* tab
  * click *Edit*
  * add new *Attribute* via *Create and Edit*

    * specify *Technical Code* (selection is non-empty only with custom modules)

  * add new Product Attribute Value via *Create and Edit*

    * specify *Technival Value*

Further information
-------------------

HTML Description: https://apps.odoo.com/apps/modules/8.0/product_attribute_code/

Tested on Odoo 8.0 25b1df2eb331275ab6bb5e572665492bbff15bdc
