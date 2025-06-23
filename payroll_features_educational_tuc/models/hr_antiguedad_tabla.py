from odoo import models, fields

class HrAntiguedadTabla(models.Model):
    _name = 'hr.antiguedad.tabla'
    _description = 'Tabla de Antigüedad'

    tipo_empleado = fields.Selection([
        ('docente', 'Docente'),
        ('no_docente', 'No Docente'),
    ], string='Tipo de Empleado', required=True)
    anios = fields.Integer('Años', required=True)
    porcentaje = fields.Float('Porcentaje', required=True)
