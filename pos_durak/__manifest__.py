{
    'name': "POS Durak",

    'summary': """Cards game for employees""",
    'images': ['images/icon.png'],

    'author': "IT-Projects LLC",
    'website': "https://en.wikipedia.org/wiki/Durak",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'communication',
    'version': '12.0.1.0.0',
    "license": "LGPL-3",

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale', 'pos_longpolling', 'web_tour'],

    # always loaded
    'data': [
        'view/durak_view.xml',
        'security/ir.model.access.csv',
        'view/test_data.xml',
        'data/ping_pong.xml',
    ],
    'qweb': [
        'static/src/xml/durak.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],

    "application": False,
    "auto_install": False,
    "installable": True,
}
