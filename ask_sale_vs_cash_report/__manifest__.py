# -*- coding: utf-8 -*-
{
    'name': "Accounting Sales vs Cash Report",
    'summary': "This is an report For Sale Vs Cash Report for Customer",

    'description': """
    Long description of module's purpose
    """,

    'author': "Asksol",
    'website': "https://www.asksol.pk",
    'category': 'Accounting',
    'version': '0.1',

    'depends': ['base','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'wizard/report_wizard.xml',
        'reports/sale_vs_cash_report.xml',
    ],
    'images': ['static/description/icon.png'],
}