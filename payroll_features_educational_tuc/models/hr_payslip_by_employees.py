from odoo import models, fields, api

class HrPayslipByEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            payslip_run = self.env['hr.payslip.run'].browse(active_id)
            nivel = payslip_run.nivel_educativo
            if nivel:
                contratos = self.env['hr.contract'].search([
                    ('nivel_educativo', '=', nivel),
                    ('state', 'in', ['open', 'pending', 'close'])
                ])
                empleados = contratos.mapped('employee_id')
                res['employee_ids'] = [(6, 0, empleados.ids)]
        return res
