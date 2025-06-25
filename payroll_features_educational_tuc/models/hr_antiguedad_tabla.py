from odoo import models, fields

class HrAntiguedadTabla(models.Model):
    _name = 'hr.antiguedad.tabla'
    _description = 'Tabla de Antigüedad'

    tipo_empleado = fields.Selection([
        ('docente', 'Docente'),
        ('no_docente', 'No Docente'),
    ], string='Tipo de Empleado', required=True)
    tipo_no_docente = fields.Selection([
        ('maestranza', 'Maestranza'),
        ('administrativo_i', 'Administrativo I'),
        ('administrativo_ii', 'Administrativo II'),
        ('jerarquicos', 'Jerárquicos'),
    ], string='Tipo No Docente')
    anios = fields.Integer('Años', required=True)
    porcentaje = fields.Float('Porcentaje', required=True)
