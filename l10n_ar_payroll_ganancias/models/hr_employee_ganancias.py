from odoo import models, fields, api
from datetime import date

class HrEmployeeGanancias(models.Model):
    _name = 'hr.employee.ganancias'
    _description = 'Ganancias 4ta Categoria'
    _inherit = ['mail.thread']

    # Campos básicos
    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True)
    year = fields.Integer('Año', default=lambda self: date.today().year)
    active = fields.Boolean(default=True)

    # ...resto del modelo...

class HrEmployeeGananciasDeduccion(models.Model):
    _name = 'hr.employee.ganancias.deduccion'
    _description = 'Deducciones Ganancias'

    ganancias_id = fields.Many2one('hr.employee.ganancias', 'Ganancias')
    name = fields.Char('Concepto', required=True)
    amount = fields.Float('Monto', required=True)
