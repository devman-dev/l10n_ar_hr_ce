# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "payroll_features",
    "version": "18.0.4.1.0",
    "category": "Accounting",
    "summary": "payroll_features",
    "sequence": -103,
    "license": "AGPL-3",
    "author":  "Devman",
    "website": "https://www.devman.com.ar",
    "depends": ['hr','hr_contract','payroll','payroll_account'],
    "data": [
        'data/sequence_data.xml',
        'views/inherit_hr_employee_view.xml',
        'views/inherit_payslip_view.xml',
        'views/inherit_payslip_run_view.xml',
        'views/libro_sueldos_view.xml',
        'views/hr_employee_libro_view.xml',
        'views/inherit_hr_salary_rule.xml',
        'views/inherit_hr_payroll_structure.xml',
        'views/inherit_hr_contract.xml',
        'views/inherit_res_company.xml',
        'views/vacacion.xml',
        'report/report.xml',
        'report/report_payslip_custom.xml',
        'security/ir.model.access.csv'
    ],
    "installable": True,
}