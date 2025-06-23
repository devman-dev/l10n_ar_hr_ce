from odoo import models, fields, api

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    sublegajo = fields.Integer('Sublegajo')

    antiguedad_global = fields.Date(
        string='Antigüedad Global',
        compute='_compute_antiguedad_global',
        store=True
    )

    @api.depends('contract_ids.antiguedad_fecha')
    def _compute_antiguedad_global(self):
        for employee in self:
            fechas = employee.contract_ids.mapped('antiguedad_fecha')
            employee.antiguedad_global = min(fechas) if fechas else False
