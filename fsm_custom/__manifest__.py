{
    'name': 'FSM - Customization',
    'version': '10.1.0',
    "category" : "Hr Manager and Project",
    'summary': '',
    "description": """
        Customization for FSM
    """,
    "author" : "Planet-odoo",
    'website': 'http://www.planet-odoo.com/',
    'depends': ['base', 'web','sale', 'field_service_dashboard', 'field_service_management', 'project_subtask', 'backend_theme_v10'],
    'data': [
             'security/ir.model.access.csv',
             'views/action_delete_view.xml',
             'views/res_partner_view.xml',
             'views/project_task_view.xml',
             'views/sale_order_fsm_view.xml',
             'data/mail_template.xml',
             'report/install_report_template.xml',
             'report/damage_report_template.xml',
             'report/feedback_report_template.xml',
             'report/modification_report_template.xml'
         ],
    'css':[
        'static/src/css/styles.css'
    ],

    'demo': [],
'qweb': [
        "static/src/xml/*.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
