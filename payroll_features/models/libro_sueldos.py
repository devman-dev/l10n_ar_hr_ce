from odoo import _, api, fields, models, tools
from datetime import datetime
import base64

class LibroSueldos(models.Model):
    _name = 'libro.sueldo'
    _description = "libro sueldos"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _rec_name = "name"

    procesamiento_liquidaciones = fields.Many2one('hr.payslip.run')
    archivo = fields.Binary('Archivo')
    name = fields.Char('')
    rectify = fields.Boolean('Rectificativo')
    comentario = fields.Char('Comentario')

    def generar_libro_sueldo(self):
        for rec in self.procesamiento_liquidaciones:

            if not self.rectify:
                nombre_archivo = "LIBRO_SUELDOS_" + str(rec.nro_procesamiento_liquidacion) + '.txt'
            else:
                nombre_archivo = "LIBRO_SUELDOS_" + str(rec.nro_procesamiento_liquidacion) + '_RE.txt'

            # CABECERA
            cuil_compania = str(self.create_uid.company_id.vat)
            ident_envio = 'SJ'
            dias_base = '30'
            periodo = datetime.strptime(str(rec.date_start), '%Y-%m-%d').strftime('%Y%m')

            liquidacion_tipo = ' '  # Inicializar con un solo espacio en blanco
            
            # Cargar el número de liquidación que sale del procesamiento y llevarlo a 5 dígitos.
            nro_liquidacion = str(rec.nro_procesamiento_liquidacion).zfill(5)

            if self.rectify:
                ident_envio = 'RE'
                dias_base = '  '  # Dos espacios en blanco
                liquidacion_tipo = ' '  # Un solo espacio en blanco
                nro_liquidacion = '     '  # Cinco espacios en blanco
            else:
                if rec.tipo_liquidacion == 'mensual' or rec.tipo_liquidacion == 'vacaciones':
                    liquidacion_tipo = 'M'
                elif rec.tipo_liquidacion in ['jornal_1', 'jornal_2']:
                    liquidacion_tipo = 'Q'

            # Armar la línea 1 (reg1 del excel)
            # Valor fijo 01 + cuit de la empresa + Sj que informa liquidación de SyJ + Periodo que surge AAAAMM + Tipo de liquidación + Número fijo + contar cantidad de empleados y formatear en 6 dígitos.
            cabecera = '01' + cuil_compania + ident_envio + periodo + liquidacion_tipo + nro_liquidacion + dias_base + str(len(rec.slip_ids)).zfill(6)

            # DETALLE
            empleados = []
            empleados_concep_salariales = []
            atrib_relacion_laboral = []
            for liq in rec.slip_ids:
                # REGISTRO 2: Datos generales de la liquidación de sueldo - Una fila por empleado con liquidación de conceptos
                # EMPELADOS
                cuil_empleado = str(liq.employee_id.cuil).replace('-', '').replace('.', '')
                legajo_empleado = str(liq.employee_id.legajo).zfill(10)
                cbu = str(liq.employee_id.cbu).replace('-', '').replace('.', '').replace(' ', '').zfill(22) if liq.employee_id.cbu else '0'.zfill(22)
                if liq.mes_vacacion:
                    cantidades_dias = str(liq.dias_vacaciones).zfill(3)
                else:
                    cantidades_dias = '000'
                cant_dias_tope_desc_trabajador = cantidades_dias
                fecha_de_pago_empleado = str(liq.fecha_de_pago).replace('-', '').replace('.', '')
                empleado_datos = '02' + cuil_empleado + legajo_empleado + ' ' * 50 + cbu + cant_dias_tope_desc_trabajador + fecha_de_pago_empleado + ' ' * 8 + '3'

                empleados.append({
                    'legajo': legajo_empleado,
                    'linea': empleado_datos
                })

                # CONCEPTOS SALARIALES
                for concept in liq.dynamic_filtered_payslip_lines:
                    if "_" in concept.code or concept.code in ['NOREM', 'ANOREM', 'PNOREM', 'BASICVAC', 'INOREM', 'ANTVAC', 'PRESVAC']:
                        continue
                    concept_empleador = str(concept.code[1:]).zfill(10)
                    concept_cantidad = "{:.2f}".format(concept.quantity).replace('.', '').zfill(5)
                    concept_unidades = ' '
                    concept_importe = "{:.2f}".format(concept.total).replace('-', '').replace('.', '').zfill(15)
                    debito_credito = 'C' if concept.total >= 0 else 'D'
                    emp_concept_salarial = '03' + cuil_empleado + concept_empleador + concept_cantidad + concept_unidades + concept_importe + debito_credito + ' ' * 6
                    empleados_concep_salariales.append(emp_concept_salarial)

                # ATRIBUTOS RELACION LABORAL
                empleado_id = liq.employee_id
                conyuge = '1' if empleado_id.conyuge else '0'
                cant_hijos = str(empleado_id.cantidad_hijos).zfill(2)
                cct = '1' if empleado_id.cct else '0'
                scvo = '1' if empleado_id.scvo else '0'
                corresponde_reduccion = '1' if empleado_id.corresponde_reduccion else '0'
                tipo_empresa = str(empleado_id.tipo_empresa)[:1] if empleado_id.tipo_empresa else '0'
                tipo_de_operacion = str(empleado_id.tipo_de_operacion)
                codigo_situacion = str(empleado_id.codigo_situacion).zfill(2)
                codigo_condicion = str(empleado_id.codigo_condicion).zfill(2)
                codigo_actividad = str(empleado_id.codigo_actividad).zfill(3)
                codigo_modalidad_contratacion = str(empleado_id.codigo_modalidad_contratacion).zfill(3)
                codigo_siniestrado = str(empleado_id.codigo_siniestrado).zfill(2)
                codigo_localidad = str(empleado_id.codigo_localidad).zfill(2)
                situacion_revista_1 = str(empleado_id.situacion_revista_1).zfill(2)
                dia_ini_sit_revista_1 = str(empleado_id.dia_ini_sit_revista_1).zfill(2)
                situacion_revista_2 = str(empleado_id.situacion_revista_2).zfill(2)
                dia_ini_sit_revista_2 = str(empleado_id.dia_ini_sit_revista_2).zfill(2)
                situacion_revista_3 = str(empleado_id.situacion_revista_3).zfill(2)
                dia_ini_sit_revista_3 = str(empleado_id.dia_ini_sit_revista_3).zfill(2)
                cant_dias_trabajados = str(empleado_id.cant_dias_trabajados).zfill(2)
                horas_trabajadas = str(empleado_id.horas_trabajadas).zfill(3)

                porcentaje_aporte_adicional_ss = str(round(empleado_id.porcentaje_aporte_adicional_ss, 2)).replace('-', '').replace('.', '').zfill(5)
                contribucion_tarea_diferencial = str(round(empleado_id.contribucion_tarea_diferencial, 2)).replace('-', '').replace('.', '').zfill(5)
                codigo_obra_social = str(empleado_id.codigo_obra_social).zfill(6)
                cantidad_adherentes = str(empleado_id.cantidad_adherentes).zfill(2)
                aporte_adicional_os = str(round(empleado_id.aporte_adicional_os, 2)).replace('-', '').replace('.', '').zfill(15)
                contribucion_adicional_os = str(round(empleado_id.contribucion_adicional_os, 2)).replace('-', '').replace('.', '').zfill(15)
                base_calculo_diferencial_aportes_os_fsr = str(round(empleado_id.base_calculo_diferencial_aportes_os_fsr, 2)).replace('-', '').replace('.', '').zfill(15)
                base_calculo_diferencial_os_fsr = str(round(empleado_id.base_calculo_diferencial_os_fsr, 2)).replace('-', '').replace('.', '').zfill(15)
                base_calculo_diferencial_lrt = str(round(empleado_id.base_calculo_diferencial_lrt, 2)).replace('-', '').replace('.', '').zfill(15)
                remuneracion_maternidad_anses = "{:.2f}".format(empleado_id.remuneracion_maternidad_anses).replace('-', '').replace('.', '').zfill(15)

                # Obtener la remuneración bruta del modelo hr.employee.libro
                libro_empleado = self.env['hr.employee.libro'].search([
                    ('employe_id', '=', liq.employee_id.id),
                    ('nro_libro', '=', rec.nro_procesamiento_liquidacion)
                ], limit=1)

                remuneracion_bruta = "{:.2f}".format(libro_empleado.remuneracion_bruta).replace('-', '').replace('.', '').zfill(15)
                base_imponible_1 = "{:.2f}".format(libro_empleado.base_imponible_1).replace('-', '').replace('.', '').zfill(15)
                base_imponible_2 = "{:.2f}".format(libro_empleado.base_imponible_2).replace('-', '').replace('.', '').zfill(15)
                base_imponible_3 = "{:.2f}".format(libro_empleado.base_imponible_3).replace('-', '').replace('.', '').zfill(15)
                base_imponible_4 = "{:.2f}".format(libro_empleado.base_imponible_4).replace('-', '').replace('.', '').zfill(15)
                base_imponible_5 = "{:.2f}".format(libro_empleado.base_imponible_5).replace('-', '').replace('.', '').zfill(15)
                base_imponible_6 = "{:.2f}".format(libro_empleado.base_imponible_6).replace('-', '').replace('.', '').zfill(15)
                base_imponible_7 = "{:.2f}".format(libro_empleado.base_imponible_7).replace('-', '').replace('.', '').zfill(15)
                base_imponible_8 = "{:.2f}".format(libro_empleado.base_imponible_8).replace('-', '').replace('.', '').zfill(15)
                base_imponible_9 = "{:.2f}".format(libro_empleado.base_imponible_9).replace('-', '').replace('.', '').zfill(15)
                base_calculo_dif_aporte_seg_social = str(round(empleado_id.base_calculo_dif_aporte_seg_social, 2)).replace('-', '').replace('.', '').zfill(15)
                base_calculo_dif_contrib_seg_social = str(round(empleado_id.base_calculo_dif_contrib_seg_social, 2)).replace('-', '').replace('.', '').zfill(15)
                base_imponible_10 = str(round(empleado_id.base_imponible_10, 2)).replace('-', '').replace('.', '').zfill(15)
                importe_a_detraer = str(round(empleado_id.importe_a_detraer, 2)).replace('-', '').replace('.', '').zfill(15)

                atrib_rel_laboral_empleado = '04' + cuil_empleado + conyuge + cant_hijos + cct + scvo + corresponde_reduccion + tipo_empresa + tipo_de_operacion + codigo_situacion + codigo_condicion + codigo_actividad + codigo_modalidad_contratacion + codigo_siniestrado + codigo_localidad + situacion_revista_1 + dia_ini_sit_revista_1 + situacion_revista_2 + dia_ini_sit_revista_2 + situacion_revista_3 + dia_ini_sit_revista_3 + cant_dias_trabajados + horas_trabajadas + porcentaje_aporte_adicional_ss + contribucion_tarea_diferencial + codigo_obra_social + cantidad_adherentes + aporte_adicional_os + contribucion_adicional_os + base_calculo_diferencial_aportes_os_fsr + base_calculo_diferencial_os_fsr + base_calculo_diferencial_lrt + remuneracion_maternidad_anses + remuneracion_bruta + base_imponible_1 + base_imponible_2 + base_imponible_3 + base_imponible_4 + base_imponible_5 + base_imponible_6 + base_imponible_7 + base_imponible_8 + base_imponible_9 + base_calculo_dif_aporte_seg_social + base_calculo_dif_contrib_seg_social + base_imponible_10 + importe_a_detraer

                atrib_relacion_laboral.append(atrib_rel_laboral_empleado)

            # CREACION DE ARCHIVO
            with open(nombre_archivo, 'w', encoding='cp1252', newline='\r\n') as file:
                file.write(cabecera + "\r\n")  # Asegúrate de que las terminaciones sean explícitas

                if not self.rectify:
                    for emp in empleados:
                        file.write(emp['linea'] + "\r\n")

                    for emp_concpt_sal in empleados_concep_salariales:
                        file.write(emp_concpt_sal + "\r\n")

                for atrib in atrib_relacion_laboral:
                    if atrib == atrib_relacion_laboral[-1]:
                        file.write(atrib)  # Última línea sin salto adicional
                    else:
                        file.write(atrib + "\r\n")

            # Leer el archivo generado en modo binario para codificarlo en base64
            with open(nombre_archivo, "rb") as file:
                out = file.read()

            self.archivo = base64.b64encode(out)
            self.name = nombre_archivo

            # Enviar el archivo al chatter como mensaje
            self.message_post(
                body=_("Archivo de libro de sueldos generado el %s por %s") % (fields.Datetime.now(), self.env.user.name),
                attachments=[(nombre_archivo, out)]
            )