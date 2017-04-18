# -*- coding: utf-8 -*-
{
    'name': 'Special offer in eCommerce',
    'version': '1.0.0',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'LGPL-3',
    'category': 'eCommerce',
    'website': 'https://yelizariev.github.io',
    'description': """
Module allows to create special offer on a web shop.

This module depends on website_sale_clear_cart module, because it's only way to delete mandatory products from /shop/cart page.

Tested on Odoo 8.0 f8d5a6727d3e8d428d9bef93da7ba6b11f344284.
    """,
    'depends': ['website_sale', 'website_sale_clear_cart'],
    'data': [
        'website_sale_special_offer_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': False
}
