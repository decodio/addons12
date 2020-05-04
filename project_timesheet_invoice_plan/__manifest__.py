# -*- coding: utf-8 -*-
{
    'name': "Project - Invoice plans",
    'category': 'Project',
    'version': '12.0.1.0.0',
    'summary': """
    Enables tracked invoicing of project timesheets
        """,

    'description': """
        - employee has assigned product for workhours
        - 
    """,

    'author': "Decodio Apllications Ltd",
    'website': "https://www.decod.io",
    "licence": "LGPL-3",

    'depends': [
        "project",
        "account",
        "hr_timesheet"
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/account_invoice.xml',
        'views/invoice_plan.xml',
        'wizard/create_project_invoice_plan_view.xml',
        'views/project.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    "external_dependencies": {
        "python": [],
        "bin": []
    },
    "auto_install": False,
    "installable": True,
}
