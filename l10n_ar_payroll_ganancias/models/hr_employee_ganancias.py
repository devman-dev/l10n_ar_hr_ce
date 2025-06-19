from odoo import models, fields, api
from datetime import date

class HrEmployeeGanancias(models.Model):
    _name = 'hr.employee.ganancias'
    _description = 'Ganancias 4ta Categoria'
    _inherit = ['mail.thread']
    
    # Campos básicos
    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True, tracking=True)
    year = fields.Integer('Año', default=lambda self: date.today().year, tracking=True)
    active = fields.Boolean(default=True)
    
    # Deducciones Personales Art. 30
    minimo_no_imponible = fields.Float('Mínimo no Imponible', tracking=True)
    deduccion_especial = fields.Float('Deducción Especial', tracking=True)
    conyuge = fields.Boolean('Cónyuge', tracking=True)
    cantidad_hijos = fields.Integer('Cantidad de Hijos', tracking=True)
    deduccion_conyuge = fields.Float('Deducción Cónyuge', compute='_compute_deducciones')
    deduccion_hijos = fields.Float('Deducción Hijos', compute='_compute_deducciones')
    
    # Deducciones Art. 85
    seguro_vida = fields.Float('Seguro de Vida', tracking=True,
                             help='Primas de seguro para caso de muerte (tope anual)')
    seguro_retiro = fields.Float('Seguro de Retiro', tracking=True)
    servicio_domestico = fields.Float('Servicio Doméstico', tracking=True)
    alquiler = fields.Float('Alquiler de Vivienda', tracking=True,
                          help='Hasta el 40% del alquiler con tope anual')
    cuota_medico = fields.Float('Cuota Médico Asistencial', tracking=True)
    donaciones = fields.Float('Donaciones', tracking=True,
                           help='Hasta el 5% de la ganancia neta')
    
    # Deducciones Adicionales
    otras_deducciones_ids = fields.One2many('hr.employee.ganancias.deduccion', 'ganancias_id', 
                                          'Otras Deducciones')
    
    # Ingresos y Totales
    remuneracion_bruta = fields.Float('Remuneración Bruta', tracking=True)
    total_deducciones = fields.Float('Total Deducciones', compute='_compute_totales', store=True)
    ganancia_neta = fields.Float('Ganancia Neta', compute='_compute_totales', store=True)
    impuesto_determinado = fields.Float('Impuesto Determinado', compute='_compute_impuesto', store=True)

    @api.depends('conyuge', 'cantidad_hijos')
    def _compute_deducciones(self):
        for rec in self:
            # Aquí irían los montos según normativa vigente
            rec.deduccion_conyuge = rec.conyuge and 100000 or 0
            rec.deduccion_hijos = rec.cantidad_hijos * 78000

    @api.depends('remuneracion_bruta', 'otras_deducciones_ids', 'minimo_no_imponible', 
                'deduccion_especial', 'deduccion_conyuge', 'deduccion_hijos')
    def _compute_totales(self):
        for rec in self:
            total_otras = sum(rec.otras_deducciones_ids.mapped('amount'))
            rec.total_deducciones = (rec.minimo_no_imponible + 
                                   rec.deduccion_especial + 
                                   rec.deduccion_conyuge + 
                                   rec.deduccion_hijos +
                                   rec.seguro_vida +
                                   rec.seguro_retiro +
                                   rec.servicio_domestico +
                                   rec.alquiler +
                                   rec.cuota_medico +
                                   rec.donaciones +
                                   total_otras)
            rec.ganancia_neta = rec.remuneracion_bruta - rec.total_deducciones

    @api.depends('ganancia_neta')
    def _compute_impuesto(self):
        for rec in self:
            # Aquí iría la tabla de alícuotas según normativa vigente
            if rec.ganancia_neta <= 0:
                rec.impuesto_determinado = 0
            else:
                # Ejemplo simplificado
                rec.impuesto_determinado = rec.ganancia_neta * 0.35

class HrEmployeeGananciasDeduccion(models.Model):
    _name = 'hr.employee.ganancias.deduccion'
    _description = 'Deducciones Ganancias'

    ganancias_id = fields.Many2one('hr.employee.ganancias', 'Ganancias')
    name = fields.Char('Concepto', required=True)
    amount = fields.Float('Monto', required=True)
    fecha = fields.Date('Fecha')
    comprobante = fields.Char('N° Comprobante')
    tipo = fields.Selection([
        ('art30', 'Deducciones Art. 30'),
        ('art85', 'Deducciones Art. 85'),
        ('otras', 'Otras Deducciones')
    ], string='Tipo de Deducción', required=True)
