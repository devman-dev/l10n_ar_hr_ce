from odoo import models, fields

class HrAntiguedadTabla(models.Model):
    _name = 'hr.antiguedad.tabla'
    _description = 'Tabla de Antigüedad'
    _rec_name = 'porcentaje'
    
    tipo_empleado = fields.Selection([
        ('director', 'Director'), ('uom', 'UOM'), ('aec', 'AEC'),
        ('fuera_convenio', 'Fuera de convenio'), ('docente', 'Docente'), 
        ('no_docente', 'No Docente'), ('jerarquico', 'Jerárquico'),
    ], string='Tipo de Empleado', required=True)
    
    tipo_no_docente = fields.Selection([
        ('maestranza', 'Maestranza'),
        ('administrativo_i', 'Administrativo I'),
        ('administrativo_ii', 'Administrativo II'),
        ('jerarquicos', 'Jerárquicos'),
    ], string='Tipo No Docente')
    
    anios = fields.Integer('Años', required=True, default=0)
    meses = fields.Integer('Años', required=True, default=0)
    porcentaje = fields.Float('Porcentaje', required=True, default=0.0)
