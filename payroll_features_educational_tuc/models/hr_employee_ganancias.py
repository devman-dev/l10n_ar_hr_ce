from odoo import models, fields, api
from datetime import date

class HrEmployeeGanancias(models.Model):
    _name = 'hr.employee.ganancias'
    _description = 'Ganancias 4ta Categoria por Empleado'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True)
    year = fields.Integer('Año', default=lambda self: date.today().year, required=True)
    active = fields.Boolean(default=True)
    
    # Deducciones Personales
    minimo_no_imponible = fields.Float('Mínimo no Imponible', tracking=True)
    deduccion_especial = fields.Float('Deducción Especial', tracking=True)
    conyuge = fields.Boolean('Cónyuge', tracking=True)
    cantidad_hijos = fields.Integer('Cantidad de Hijos', tracking=True)
    
    # Deducciones del Art. 23
    seguro_vida = fields.Float('Seguro de Vida', tracking=True)
    servicio_domestico = fields.Float('Servicio Doméstico', tracking=True)
    alquiler = fields.Float('Alquiler de Vivienda', tracking=True)
    cuota_medico = fields.Float('Cuota Médico Asistencial', tracking=True)
    donaciones = fields.Float('Donaciones', tracking=True)
    
    # Otras Deducciones
    otras_deducciones_ids = fields.One2many('hr.employee.ganancias.deduccion', 'ganancias_id', 'Otras Deducciones')
    
    # Totales
    ganancia_bruta = fields.Float('Ganancia Bruta', compute='_compute_totales', store=True)
    total_deducciones = fields.Float('Total Deducciones', compute='_compute_totales', store=True)
    ganancia_neta = fields.Float('Ganancia Neta', compute='_compute_totales', store=True)

    @api.depends('otras_deducciones_ids', 'minimo_no_imponible', 'deduccion_especial')
    def _compute_totales(self):
        for rec in self:
            # Aquí irá la lógica de cálculo según normativa vigente
            pass

class HrEmployeeGananciasDeduccion(models.Model):
    _name = 'hr.employee.ganancias.deduccion'
    _description = 'Deducciones Adicionales Ganancias'

    ganancias_id = fields.Many2one('hr.employee.ganancias', 'Ganancias')
    name = fields.Char('Concepto', required=True)
    amount = fields.Float('Monto', required=True)
    fecha = fields.Date('Fecha')
    comprobante = fields.Char('N° Comprobante')
