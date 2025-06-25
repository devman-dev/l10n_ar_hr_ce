from odoo import models, fields, api

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    nivel_educativo = fields.Selection([
        ('primario', 'Primario'),
        ('secundario', 'Secundario'),
        ('terciario', 'Terciario'),
        ('primario_no_subvencionado', 'Primario no subvencionado'),
        ('secundario_no_subvencionado', 'Secundario no subvencionado'),
        ('terciario_no_subvencionado', 'Terciario no subvencionado'),
        ('no_docente_administrativo', 'No docente - Administrativo I'),
        ('no_docente_administrativo', 'No docente - Administrativo II'),
        ('no_docente_jerarquico', 'No docente - Jerárquico'),
        ('no_docente_maestranza', 'No docente - Maestranza'),
    ], string='Nivel Educativo')

    @api.model
    def _get_contracts(self, employees, date_start, date_end):
        contracts = super()._get_contracts(employees, date_start, date_end)
        if self.nivel_educativo:
            contracts = contracts.filtered(lambda c: c.nivel_educativo == self.nivel_educativo)
        return contracts
