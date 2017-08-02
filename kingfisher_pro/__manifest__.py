# -*- coding: utf-8 -*-
# Part of BiztechCS. See LICENSE file for full copyright and licensing details.

{
    'name': 'Kingfisher Pro Fashion',
    'description': 'Kingfisher Pro Fashion',
    'category': 'Theme/Ecommerce',
    'version': '10.0.1.0.1',
    'author': 'BiztechCS',
    'website': 'https://www.biztechconsultancy.com',
    'depends': [
        'website_sale',
        'mass_mailing',
        'website_blog',
    ],
    'data': [
        'views/assets.xml',
        'security/ir.model.access.csv',
        'views/slider_view.xml',
        'views/product_view.xml',
        'views/snippets.xml',
        'views/website_config_view.xml',
        'views/theme_customize.xml',
        'data/data.xml',
        'views/theme.xml',
    ],
    'demo': [
        # 'data/demo_homepage.xml',
    ],
    'application': True,
    'live_test_url': 'http://theme-kingfisher-pro-fashion.biztechconsultancy.com',
    'images': ['static/description/splash-screen.png'],
    'price': 109.00,
    'currency': 'EUR',
}
