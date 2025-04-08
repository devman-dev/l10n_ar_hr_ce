from datetime import date, datetime
from dateutil import relativedelta

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'
    _description = "Inherit employee"

    anios = fields.Integer('Años de antiguedad', compute='_calcular_antiguedad')
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
                                     ('8_decreto_1212_03_afa_clubes', '8-Decreto 1212/03 - AFA Clubes')])
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

    regla_a_cuenta_futuros = fields.Boolean('regla a cuenta futuros')

    employee_libro = fields.One2many('hr.employee.libro', 'employe_id', string="Libro de Sueldos")

    @api.model
    def create(self, vals):
        vals['legajo'] = self.env['ir.sequence'].next_by_code('hr.employee') or _('New')
        return super(HrEmployeeInherit, self).create(vals)

    @api.constrains('cuil')
    def check_cuil(self):
        for rec in self:
            if rec.cuil:
                if len(rec.cuil) > 13 or len(rec.cuil) < 13:
                    raise ValidationError('La longitud del campo CUIL es incorrecta.')

                if rec.cuil[2:3] != '-' or rec.cuil[11:12] != '-':
                    raise ValidationError('El formato del campo CUIL debe ser el siguiente: 00-00000000-0.')



    @api.constrains('cbu', 'cantidad_hijos', 'tipo_de_operacion', 'codigo_situacion', 'codigo_condicion',
                    'codigo_actividad', 'codigo_modalidad_contratacion', 'codigo_siniestrado', 'codigo_localidad',
                    'situacion_revista_1', 'dia_ini_sit_revista_1', 'situacion_revista_2', 'dia_ini_sit_revista_2',
                    'situacion_revista_3', 'dia_ini_sit_revista_3', 'cant_dias_trabajados', 'horas_trabajadas',
                    'codigo_obra_social', 'cantidad_adherentes')
    def cant_numeros_cbu(self):
        for rec in self:
            if len(self.cbu) != 22:
                raise ValidationError('La longitud del campo CBU es incorrecta.')
            if self.cbu.isdigit():
                pass
            else:
                raise ValidationError('El campo CBU debe contener solo números.')

            if len(str(self.cantidad_hijos)) > 2:
                raise ValidationError('La longitud del campo Cant.Hijos es mayor a dos dígitos.')

            if len(str(self.tipo_de_operacion)) > 1:
                raise ValidationError('La longitud del campo Tipo de operación es mayor a un dígito.')

            if len(str(self.codigo_situacion)) > 2:
                raise ValidationError('La longitud del campo Código Situación es mayor a dos dígitos.')

            if len(str(self.codigo_condicion)) > 2:
                raise ValidationError('La longitud del campo Código Condición es mayor a dos dígitos.')

            if len(str(self.codigo_actividad)) > 3:
                raise ValidationError('La longitud del campo Código actividad es mayor a tres dígitos.')

            if len(str(self.codigo_modalidad_contratacion)) > 3:
                raise ValidationError('La longitud del campo Código modalidad contratación es mayor a tres dígitos.')

            if len(str(self.codigo_siniestrado)) > 2:
                raise ValidationError('La longitud del campo Código Siniestrado es mayor a dos dígitos.')

            if len(str(self.codigo_localidad)) > 2:
                raise ValidationError('La longitud del campo Código localidad es mayor a dos dígitos.')

            if len(str(self.situacion_revista_1)) > 2:
                raise ValidationError('La longitud del campo Situación revista 1 es mayor a dos dígitos.')

            if len(str(self.dia_ini_sit_revista_1)) > 2:
                raise ValidationError('La longitud del campo Día inicio situación de revista 1 es mayor a dos dígitos.')

            if len(str(self.situacion_revista_2)) > 2:
                raise ValidationError('La longitud del campo Situación revista 2 es mayor a dos dígitos.')

            if len(str(self.dia_ini_sit_revista_2)) > 2:
                raise ValidationError('La longitud del campo Día inicio situación de revista 2 es mayor a dos dígitos.')

            if len(str(self.situacion_revista_3)) > 2:
                raise ValidationError('La longitud del campo Situación revista 3 es mayor a dos dígitos.')

            if len(str(self.dia_ini_sit_revista_3)) > 2:
                raise ValidationError('La longitud del campo Día inicio situación de revista 3 es mayor a dos dígitos.')

            if len(str(self.cant_dias_trabajados)) > 2:
                raise ValidationError('La longitud del campo Cant. Días trabajados es mayor a dos dígitos.')

            if len(str(self.horas_trabajadas)) > 3:
                raise ValidationError('La longitud del campo Horas trabajadas es mayor a tres dígitos.')

            if len(str(self.codigo_obra_social)) > 6:
                raise ValidationError('La longitud del campo Código obra social es mayor a seis dígitos.')

            if len(str(self.cantidad_adherentes)) > 2:
                raise ValidationError('La longitud del campo Cant. Adherentes es mayor a dos dígitos.')

    def _calcular_antiguedad(self):
        tiempo_transc = ''
        if self.contract_id.date_start:
            fecha_inicial = self.contract_id.date_start
            fecha_fin = datetime.now()
            tiempo_transc = relativedelta.relativedelta(fecha_fin, fecha_inicial)

            if tiempo_transc.years >= 1:
                self.anios = tiempo_transc.years
            else:
                if tiempo_transc.months >= 6:
                    self.anios = 1
                else:
                    self.anios = 0
        else:
            self.anios = 0


