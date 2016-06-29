# -*- coding: utf-8 -*-
{
    'name': "Vehicle parts svg",

    'summary': """displays parts on interactive svg""",


    'author': "IT-Projects LLC, Veronika Kotovich",
    'license': 'LGPL-3',
    'website': "https://yelizariev.github.io",

    'category': 'Managing vehicles',
    'version': '0.1',

    'depends': ['base', 'report', 'fleet', 'web_form_svg'],
    'external_dependencies' : {
        'python' : ['wand'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_vehicle.xml',
        'views/fleet_vehicle_report.xml',
        'data/fleet_vehicle_part.xml',
    ],
    'demo': [
    ],
    'installable': True
}
