from odoo import models, fields, api
from datetime import date

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    sublegajo = fields.Integer('Sublegajo')

    antiguedad_global_anios = fields.Integer(
        string='Antigüedad Global (Años)',
        compute='_compute_antiguedad_global_anios',
        store=True
    )

    @api.depends('contract_ids.date_start')
    def _compute_antiguedad_global_anios(self):
        for employee in self:
            fechas = employee.contract_ids.mapped('date_start')
            if fechas:
                fecha_min = min(fechas)
                hoy = date.today()
                diff = hoy.year - fecha_min.year - ((hoy.month, hoy.day) < (fecha_min.month, fecha_min.day))
                employee.antiguedad_global_anios = max(diff, 0)
            else:
                employee.antiguedad_global_anios = 0
