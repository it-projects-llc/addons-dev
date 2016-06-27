{
    'name': "SVG Widget",
    'summary': """SVG Widget""",
    'version': '1.0.0',
    'author': 'IT-Projects LLC, Veronika Kotovich',
    'license': 'LGPL-3',
    'category': 'Tools',
    'website': 'https://twitter.com/vkotovi4',
    'depends': [
        'web',
    ],
    'data': [
        # 'security/web_debranding_security.xml',
        # 'security/ir.model.access.csv',
        # 'data.xml',
        'views.xml',
        # 'js.xml',
        # 'pre_install.yml',
        ],
    'qweb': [
         "static/src/xml/*.xml",
    ],
    'auto_install': False,
    'installable': True
}
