{
    'name': 'HR Payslip Excel Export for Avangard Bank',
    'summary' : 'Allows to export HR Payslips as excel files',
    'version': '1.0.0',
    'category': 'Human Resources',
    'author': 'IT-Projects LLC',
    'license': 'GPL-3',
    'website': 'https://yelizariev.github.io',
    'description': """Module allows to export HR Payslips as excel files showing net amount.""",
    'depends': ['base','hr_payroll','hr_payslip_net'],
    'data': ['wizard/export_wizard.xml'],
    'installable': True,
}
