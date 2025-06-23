# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Portal',
    'summary': 'Employee Portal',
    'sequence': 9001,
    'category': 'Hidden',
    'description': """""",
    # 'depends': ['base', 'web', 'bus', 'website', 'web_editor', 'http_routing', 'mail', 'auth_signup', 'hr', 'payroll', 'calendar', 'knowledge', 'hr_holidays'],
    'depends': ['base', 'web', 'bus', 'website', 'web_editor', 'http_routing', 'mail', 'auth_signup', 'hr', 'payroll', 'calendar', 'hr_holidays'],
    'data': [
        'data/res_groups.xml',
        'security/ir.model.access.csv',
        'views/portal_employee_templates.xml',
        'views/hr_employee_views.xml',
    ],
    'license': 'LGPL-3',
}
