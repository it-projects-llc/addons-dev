# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Field Service Management",
    "version": "1.51",
    "category": "Hr Manager and Project",
    "license": "AGPL-3",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.serpentcs.com",
    "description": """
        This module allows you to create a new field service management system.
        ======================================================================
        
        Field Service (formerly Service Online) drives profitability by automating 
        the process of dispatching field technicians to service calls in remote 
        locations. Field Service improves customer satisfaction by more accurately 
        predicting a window to promise for service delivery, and it contains the Assignment 
        automatically to eliminate guesswork surrounding qualification, availability and
        suggest the best service person of each field service technician.
            """,
    "depends": ["hr", "project", "crm", "sale_timesheet", "hr_timesheet", "document"],
    "demo": [
        "demo/service_skill_demo.xml",
        "demo/res_users_demo.xml",
        "demo/city_demo.xml",
        "demo/area_demo.xml",
        "demo/zone_demo.xml",
        "demo/jobs_demo.xml",
        "demo/employee_data.xml",
        "demo/emp_skill_line_demo.xml",

    ],
    "data": [
        "security/fsm_security.xml",
        "security/ir.model.access.csv",
        "data/job_sequence.xml",
        "data/stage_data.xml",
        "views/menuitems_hide.xml",
        "report/job_report_template.xml",
        "report/job_report_register.xml",
        "report/job_report_paperformat.xml",
        "views/employee_view.xml",
        "views/menuitems.xml",
        "views/feedback_view.xml",
        "views/task.xml",
        "views/task_type.xml",
        "views/res_users.xml",
        "views/res_partner.xml",
        "views/res_company.xml",
        "views/area_area_view.xml",
        "views/city_city_view.xml",
        "views/zone_zone_view.xml",
        "views/project.xml",
        "wizard/suggested_serviceman.xml",
        "data/notify_customer_job_template.xml",
        "data/notify_serviceman_job_template.xml",
        "data/job_delete_data.xml",
    ],
    "installable": True,
    "auto_install": False,
}
