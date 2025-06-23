from odoo import models, fields, api

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    nivel_educativo = fields.Selection([
        ('inicial', 'Inicial'),
        ('primario', 'Primario'),
        ('secundario', 'Secundario'),
        ('terciario', 'Terciario'),
        ('universitario', 'Universitario'),
    ], string='Nivel Educativo')

    @api.model
    def _get_contracts(self, employees, date_start, date_end):
        contracts = super()._get_contracts(employees, date_start, date_end)
        if self.nivel_educativo:
            contracts = contracts.filtered(lambda c: c.nivel_educativo == self.nivel_educativo)
        return contracts
