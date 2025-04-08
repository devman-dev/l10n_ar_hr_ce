from odoo import api, fields, models, tools
from datetime import *

class LibroSueldos(models.Model):
    _name = 'hr.employee.libro'
    _description = "libro sueldos por empleado"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _rec_name = "employe_id"

    employe_id = fields.Many2one('hr.employee', 'Empleado')
    procesamiento_liquidaciones = fields.Many2one('hr.payslip.run', string='Procesamiento de liquidacion', compute='_compute_procesamiento_liquidaciones')
    nro_libro = fields.Integer('Numero de libro de sueldo')
    anios = fields.Integer('Años de antiguedad')
    antiguedad_anterior = fields.Boolean('Antiguedad Anterior')
    anios_ant = fields.Integer('Años de antiguedad anterior')
    legajo = fields.Integer('Legajo')
    cuil = fields.Char('C.U.I.L')
    cbu = fields.Char('CBU', size=24)

    tipo_empleado = fields.Selection([('director', 'Director'), ('uom', 'UOM'), ('aec', 'AEC'),
                                      ('fuera_convenio', 'Fuera de convenio')])

    conyuge = fields.Boolean('Cónyuge')
    cantidad_hijos = fields.Integer('Cant.Hijos', size=2)
    cct = fields.Boolean('CCT')
    scvo = fields.Boolean('SCVO')
    corresponde_reduccion = fields.Boolean('Corresponde reducción')
    tipo_empresa = fields.Selection([('0_administracion_publica', '0 - Administración Pública'),
                                     ('1_decreto_814_01_art2_inc_b', '1-Decreto 814/01, Art2 Inc.B'),
                                     ('2_servicios_eventuales_art2_inc_b', '2-Servicios Eventuales, Art2 Inc.B'),
                                     ('4_decreto_814_01_art2_inc_a', '4-Decreto 814/01, Art2 Inc.A'),
                                     ('5_servicios_eventuales_art2_inc_a', '5-Servicios Eventuales, Art2 Inc.A'),
                                     ('7_enseñanza_privada', '7-Enseñanza Privada'),
                                     ('8_decreto_1212_03_afa_clubes', '8-Decreto 1212/03 - AFA Clubes')], default='1_decreto_814_01_art2_inc_b')
    tipo_de_operacion = fields.Integer('Tipo de Operación', default=0)
    codigo_situacion = fields.Char('Código situación')
    codigo_condicion = fields.Char('Código condición')
    codigo_actividad = fields.Char('Código actividad')
    codigo_modalidad_contratacion = fields.Char('Código modalidad contratación')
    codigo_siniestrado = fields.Char('Código siniestrado')
    codigo_localidad = fields.Char('Código localidad')
    situacion_revista_1 = fields.Char('Situación de revista 1')
    dia_ini_sit_revista_1 = fields.Char('Día inicio Situación de revista 1')
    situacion_revista_2 = fields.Char('Situación de revista 2')
    dia_ini_sit_revista_2 = fields.Char('Día inicio Situación de revista 2')
    situacion_revista_3 = fields.Char('Situación de revista 3')
    dia_ini_sit_revista_3 = fields.Char('Día inicio Situación de revista 3')
    cant_dias_trabajados = fields.Char('Cant. días trabajados')
    horas_trabajadas = fields.Char('Horas trabajadas')
    porcentaje_aporte_adicional_ss = fields.Float('Porcentaje aporte adicional SS')
    contribucion_tarea_diferencial = fields.Float('Contribución tarea diferencial')
    codigo_obra_social = fields.Char('Código obra social')
    cantidad_adherentes = fields.Char('Cant. Adherentes')
    aporte_adicional_os = fields.Float('Aporte adicional O S')
    contribucion_adicional_os = fields.Float('Contribución adicional O S')
    base_calculo_diferencial_aportes_os_fsr = fields.Float('Base cálculo diferencial aportes OS Y FSR')
    base_calculo_diferencial_os_fsr = fields.Float('Base cálculo diferencial OS Y FSR')
    base_calculo_diferencial_lrt = fields.Float('Base cálculo diferencial LRT')
    remuneracion_maternidad_anses = fields.Float('Remuneración maternidad ANSeS')
    remuneracion_bruta = fields.Float('Remuneración bruta')
    base_imponible_1 = fields.Float('Base imponible 1')
    base_imponible_2 = fields.Float('Base imponible 2')
    base_imponible_3 = fields.Float('Base imponible 3')
    base_imponible_4 = fields.Float('Base imponible 4')
    base_imponible_5 = fields.Float('Base imponible 5')
    base_imponible_6 = fields.Float('Base imponible 6')
    base_imponible_7 = fields.Float('Base imponible 7')
    base_imponible_8 = fields.Float('Base imponible 8')
    base_imponible_9 = fields.Float('Base imponible 9')
    base_calculo_dif_aporte_seg_social = fields.Float('Base cálculo diferencial aporte seguro social')
    base_calculo_dif_contrib_seg_social = fields.Float('Base cálculo diferencial contribución seguro social')
    base_imponible_10 = fields.Float('Base imponible 10')
    importe_a_detraer = fields.Float('Importe a detraer')

    @api.depends('nro_libro')
    def _compute_procesamiento_liquidaciones(self):
        for record in self:
            record.procesamiento_liquidaciones = self.env['hr.payslip.run'].search([('nro_procesamiento_liquidacion', '=', record.nro_libro)], limit=1)

