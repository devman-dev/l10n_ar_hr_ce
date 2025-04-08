from odoo import _, api, fields, models, tools
import num2words
from num2words import num2words
from datetime import *
import logging

from .base_browsable import (
    BaseBrowsableObject,
    BrowsableObject,
    InputLine,
    Payslips,
    WorkedDays,
)

_logger = logging.getLogger(__name__)

class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'
    _description = "Payslip Inherit"

    neto = fields.Float('Neto')
    haberes_remunerativos = fields.Float('Haberes remunerativos')
    haberes_no_remunerativos = fields.Float('Haberes no remunerativos')
    descuentos = fields.Float('Retenciones')
    basico = fields.Float('Remuneración')
    remuneracion_bruta = fields.Float('Remuneración Bruta')
    total_en_texto = fields.Char('Total en texto')
    fecha_de_pago = fields.Date('Fecha de pago')
    lugar_de_pago = fields.Char('Lugar de Pago')
    nro_recibo = fields.Char('N° de recibo')
    banco_diario_contable_id = fields.Many2one('account.journal', 'Banco últ. depósito', domain="[('type', '=', 'bank')]")
    fecha_ult_deposito = fields.Date('Fecha últ. depósito')
    periodo_ult_deposito = fields.Date('Período últ. depósito')
    periodo_mes_anio = fields.Char('Período últ. depósito', compute='_transformar_fecha_periodo')
    tipo_liquidacion = fields.Selection([('mensual', 'Mensual'), ('jornal_1', 'Jornal(1° Quincena)'), ('jornal_2', 'Jornal(2° Quincena)'), ('aguinaldo', 'Aguinaldo'), ('vacaciones', 'Vacaciones'),
                                         ('lic_matrimonio', 'Lic. Matrimonio'), ('anticipo', 'Anticipo'), ('ajuste', 'Ajuste'), ('liq_final', 'Liquidación Final')])
    calculo = fields.Float('calculo', compute='_calcular_totales')
    dias_vacaciones = fields.Integer('Dias de vacaciones')
    mes_vacacion = fields.Boolean('Mes Vacacion', default=False)

    ajuste = fields.Float('Ajuste')

    @api.model
    def create(self, vals):
        vals['nro_recibo'] = self.env['ir.sequence'].next_by_code('hr.payslip') or _('New')
        return super(HrPayslipInherit, self).create(vals)

    @api.depends('fecha_de_pago')
    def _calcular_totales(self):
        if self.line_ids:
            for rec in self.line_ids:
                self.calculo = 0
                if rec.code == 'C_1000':
                    self.neto = rec.total
                    self.calculo = 0
                    pre = round(float(self.neto), 2)
                    text = ''
                    entire_num = int((str(pre).split('.'))[0])
                    decimal_num = int((str(pre).split('.'))[1])
                    if decimal_num < 10:
                        decimal_num = decimal_num * 10
                    text += num2words(entire_num, lang='es')
                    text += ' con '
                    text += num2words(decimal_num, lang='es')

                    self.total_en_texto = text.upper()

                if rec.code == 'C_1001':
                    self.haberes_remunerativos = rec.total
                if rec.code == 'C_1002':
                    self.haberes_no_remunerativos = rec.total
                if rec.code == 'C_1003':
                    self.descuentos = rec.total
                if rec.code == 'C1':
                    self.basico = rec.total
                if rec.code == 'C_1004':
                    self.employee_id.remuneracion_bruta = rec.total
                    self.remuneracion_bruta = rec.total
        else:
            self.neto = 0
            self.haberes_remunerativos = 0
            self.haberes_no_remunerativos = 0
            self.descuentos = 0
            self.basico = 0
            self.calculo = 0
            self.remuneracion_bruta = 0

    @api.depends('periodo_ult_deposito')
    def _transformar_fecha_periodo(self):
        for rec in self:
            if self.periodo_ult_deposito:
                self.periodo_mes_anio = datetime.strptime(str(self.periodo_ult_deposito), '%Y-%m-%d').strftime('%m/%Y')
                print(self.periodo_mes_anio)
            else:
                self.periodo_mes_anio = ''


    def compute_sheet(self):
        for payslip in self:
            # delete old payslip lines
            payslip.line_ids.unlink()
            # write payslip lines
            number = payslip.number or self.env["ir.sequence"].next_by_code(
                "salary.slip"
            )
            lines = [(0, 0, line) for line in list(payslip.get_lines_dict().values())]

            total_en_texto = float(0)
            haberes_remunerativos = float(0)
            haberes_no_remunerativos = float(0)
            descuentos = float(0)
            basico = float(0)
            neto = float(0)

            base_imp_1_5 = []
            base_imp_2_3 = []
            base_imp_4 = []
            base_imp_8 = []
            base_imp_9 = []
            base_imp_6 = []
            base_imp_7 = []

            for e in lines:
                if e[2]['code'] == 'C_1000':
                    neto = e[2]['total']

                    pre = round(float(neto), 2)
                    text = ''
                    entire_num = int((str(pre).split('.'))[0])
                    decimal_num = int((str(pre).split('.'))[1])
                    if decimal_num < 10:
                        decimal_num = decimal_num * 10
                    text += num2words(entire_num, lang='es')
                    text += ' con '
                    text += num2words(decimal_num, lang='es')

                    total_en_texto = text.upper()

                if e[2]['code'] == 'C_1001':
                    haberes_remunerativos = e[2]['total']
                if e[2]['code'] == 'C_1002':
                    haberes_no_remunerativos = e[2]['total']
                if e[2]['code'] == 'C_1003':
                    descuentos = e[2]['total']
                if e[2]['code'] == 'C1':
                    basico = e[2]['total']
                if e[2]['code'] == 'C_1004':
                    payslip.employee_id.remuneracion_bruta = e[2]['total']

                if e[2]['code'] == 'C404':
                    e[2]['amount'] = self.ajuste
                    e[2]['total'] = self.ajuste



                # AGREGAR FUNCIONES Y CALCULOS PARA ARMAR BASES IMPONIBLES
                regla_salarial = ''
                try:
                    domain = [('code', '=', e[2]['code'])]
                    regla_salarial = self.env['hr.salary.rule'].sudo().search(domain)

                except Exception as error_buscando_regla:
                    print('error buscando regla salarial', str(error_buscando_regla))

                if regla_salarial:

                    if regla_salarial.category_id.code == 'BASIC':
                        base_imp_1_5.append(e[2]['total'])
                        base_imp_2_3.append(e[2]['total'])
                        base_imp_4.append(e[2]['total'])
                        base_imp_8.append(e[2]['total'])
                        base_imp_9.append(e[2]['total'])

                    if regla_salarial.category_id.code == 'HAB_NO_REM':

                        # BASE IMPONIBLE 1 y 5

                        if regla_salarial.aporte_sipa or regla_salarial.aporte_inssjyp:
                            if e[2]['total'] not in base_imp_1_5:
                                base_imp_1_5.append(e[2]['total'])
                            else:
                                pass

                        # BASE IMPONIBLE 4

                        if regla_salarial.aporte_obra_social or regla_salarial.aporte_fsr:
                            if e[2]['total'] not in base_imp_4:
                                base_imp_4.append(e[2]['total'])
                            else:
                                pass

                        # BASE IMPONIBLE 2 Y 3

                        if regla_salarial.contrib_sipa or regla_salarial.contrib_inssjyp or regla_salarial.contrib_renatea or regla_salarial.contrib_asignaciones_familiares or regla_salarial.contrib_fondo_nacional_empleo:
                            if e[2]['total'] not in base_imp_2_3:
                                base_imp_2_3.append(e[2]['total'])
                            else:
                                pass

                        # BASE IMPONIBLE 8

                        if regla_salarial.contrib_obra_social or regla_salarial.contrib_fsr:
                            if e[2]['total'] not in base_imp_8:
                                base_imp_8.append(e[2]['total'])
                            else:
                                pass

                        # BASE IMPONIBLE 9

                        if regla_salarial.contrib_ley_riego_trabajo:
                            if e[2]['total'] not in base_imp_9:
                                base_imp_9.append(e[2]['total'])
                            else:
                                pass

                    # BASE IMPONIBLE 6

                    if regla_salarial.aporte_regimenes_diferenciales:
                        if e[2]['total'] not in base_imp_6:
                            base_imp_6.append(e[2]['total'])
                        else:
                            pass

                    # BASE IMPONIBLE 7

                    if regla_salarial.aporte_regimenes_especiales:
                        if e[2]['total'] not in base_imp_7:
                            base_imp_7.append(e[2]['total'])
                        else:
                            pass

            payslip.employee_id.base_imponible_1 = sum(base_imp_1_5) # SUMAR BASE DIFERENCIAL DE APORTES DE SEGURIDAD SOCIAL

            payslip.employee_id.base_imponible_5 = sum(base_imp_1_5) # SUMAR BASE DIFERENCIAL DE APORTES DE SEGURIDAD SOCIAL

            payslip.employee_id.base_imponible_4 = sum(base_imp_4) # SUMAR BASE DIFERENCIAL DE APORTE OBRA SOCIAL

            payslip.employee_id.base_imponible_2 = sum(base_imp_2_3) # SUMAR BASE DIFERENCIAL DE CONTRIBUCION DEL CUADRO DE SEGURIDAD SOCIAL

            payslip.employee_id.base_imponible_3 = sum(base_imp_2_3) # SUMAR BASE DIFERENCIAL DE CONTRIBUCION DEL CUADRO DE SEGURIDAD SOCIAL

            payslip.employee_id.base_imponible_8 = sum(base_imp_8) # SUMAR BASE DIFERENCIAL DE CONTRIBUCION DE OBRA SOCIAL

            payslip.employee_id.base_imponible_9 = sum(base_imp_9) # SUMAR BASE DIFERENCIAL DE LRT

            payslip.write(
                    {
                        "line_ids": lines,
                        "number": number,
                        "state": "verify",
                        "compute_date": fields.Date.today(),
                        "basico": round(basico, 2),
                        "total_en_texto": total_en_texto,
                        "haberes_remunerativos": round(haberes_remunerativos, 2),
                        "haberes_no_remunerativos": round(haberes_no_remunerativos, 2),
                        "descuentos": round(descuentos, 2),
                        "neto":  round(neto, 2)
                    }
                )

            # Lógica para crear o actualizar registros en hr.employee.libro
            libro_model = self.env['hr.employee.libro']
            libro = libro_model.search(
                [('employe_id', '=', payslip.employee_id.id), ('nro_libro', '=', payslip.payslip_run_id.nro_procesamiento_liquidacion)], limit=1)

            valores = {
                "base_imponible_1": sum(base_imp_1_5),
                "base_imponible_5": sum(base_imp_1_5),
                "base_imponible_4": sum(base_imp_4),
                "base_imponible_2": sum(base_imp_2_3),
                "base_imponible_3": sum(base_imp_2_3),
                "base_imponible_8": sum(base_imp_8),
                "base_imponible_9": sum(base_imp_9),
            }

            if libro:
                # Actualizar valores si existe el registro
                libro.write(valores)
            else:
                # Crear nuevo registro si no existe
                valores.update({
                    "employe_id": payslip.employee_id.id,
                    "nro_libro": payslip.payslip_run_id.nro_procesamiento_liquidacion,
                })
                libro_model.create(valores)

        return True

    def _get_lines_dict(
            self, rule, localdict, lines_dict, key, values, previous_amount
    ):
        if rule.code == 'C404':
            values["amount"] = self.ajuste

        if rule.code == 'C15':
            for reg in rule.custom_amount_ids:
                if reg.employee_id.id == self.employee_id.id:
                    values["amount"] = reg.importe

        #if rule.code == 's_agosto':
        #    for reg in rule.custom_amount_ids:
        #        if reg.employee_id.id == self.employee_id.id:
        #            values["amount"] = reg.importe

        #if rule.code == 's_septiem':
        #    for reg in rule.custom_amount_ids:
        #        if reg.employee_id.id == self.employee_id.id:
        #            values["amount"] = reg.importe

        if rule.custom_amount == True:
            for reg in rule.custom_amount_ids:
                if reg.employee_id.id == self.employee_id.id:
                    values["amount"] = reg.importe

        total = values["quantity"] * values["rate"] * values["amount"] / 100.0
        values["total"] = total
        # set/overwrite the amount computed for this rule in the localdict
        if rule.code:
            localdict[rule.code] = total
            localdict["rules"].dict[rule.code] = rule
            localdict["result_rules"].dict[rule.code] = BaseBrowsableObject(values)
        # sum the amount for its salary category
        localdict = self._sum_salary_rule_category(
            localdict, rule.category_id, total - previous_amount
        )
        # create/overwrite the line in the temporary results
        line_dict = {
            "salary_rule_id": rule.id,
            "employee_id": localdict["employee"].id,
            "contract_id": localdict["contract"].id,
            "code": rule.code,
            "category_id": rule.category_id.id,
            "sequence": rule.sequence,
            "appears_on_payslip": rule.appears_on_payslip,
            "parent_rule_id": rule.parent_rule_id.id,
            "condition_select": rule.condition_select,
            "condition_python": rule.condition_python,
            "condition_range": rule.condition_range,
            "condition_range_min": rule.condition_range_min,
            "condition_range_max": rule.condition_range_max,
            "amount_select": rule.amount_select,
            "amount_fix": rule.amount_fix,
            "amount_python_compute": rule.amount_python_compute,
            "amount_percentage": rule.amount_percentage,
            "amount_percentage_base": rule.amount_percentage_base,
            "register_id": rule.register_id.id,
        }
        line_dict.update(values)
        lines_dict[key] = line_dict
        return localdict, lines_dict

    def _sum_salary_rule_category(self, localdict, category, amount):
        self.ensure_one()
        if category.parent_id:
            localdict = self._sum_salary_rule_category(
                localdict, category.parent_id, amount
            )
        if category.code:
            localdict["categories"].dict[category.code] = (
                localdict["categories"].dict.get(category.code, 0) + amount
            )
        return localdict

    def button_recompute_libro(self):
        for payslip in self:

            payslip_run = payslip.payslip_run_id.name
            payslip_number = payslip.number
            payslip_employee = payslip.employee_id.name
            _logger.info('Payslip name: %s, %s, %s', payslip_employee, payslip_run, payslip_number)
            
            line_ids = payslip.line_ids

            _logger.info('Payslip lines: %s', line_ids)

            base_imp_1_5 = []
            base_imp_2_3 = []
            base_imp_4 = []
            base_imp_8 = []
            base_imp_9 = []
            base_imp_6 = []
            base_imp_7 = []
            remuneracion_bruta = 0.0
            neto = 0.0
            haberes_remunerativos = 0.0
            haberes_no_remunerativos = 0.0
            descuentos = 0.0
            basico = 0.0

            for line in line_ids:
                _logger.info('Payslip line: %s', line)
                if line.code == 'C_1000':
                    neto += line.total
                if line.code == 'C_1001':
                    haberes_remunerativos += line.total
                if line.code == 'C_1002':
                    haberes_no_remunerativos += line.total
                if line.code == 'C_1003':
                    descuentos += line.total
                if line.code == 'C1':
                    basico += line.total
                if line.code == 'C_1004':
                    remuneracion_bruta += line.total
                    _logger.info('Composición de remuneracion_bruta: %s', remuneracion_bruta)
                _logger.info('Composición de NETO: %s', neto)

                if line.category_id:
                    if line.category_id.code == 'BASIC':
                        base_imp_1_5.append(line.total)
                        base_imp_2_3.append(line.total)
                        base_imp_4.append(line.total)
                        base_imp_8.append(line.total)
                        base_imp_9.append(line.total)

                        _logger.info('Composición de base_imp_1_5: %s', base_imp_1_5)
                        _logger.info('Composición de base_imp_2_3: %s', base_imp_2_3)
                        _logger.info('Composición de base_imp_4: %s', base_imp_4)
                        _logger.info('Composición de base_imp_8: %s', base_imp_8)
                        _logger.info('Composición de base_imp_9: %s', base_imp_9)

                    if line.category_id.code == 'HAB_NO_REM':
                        if line.salary_rule_id.aporte_sipa or line.aporte_inssjyp:
                            base_imp_1_5.append(line.total)
                        if line.salary_rule_id.aporte_obra_social or line.aporte_fsr:
                            base_imp_4.append(line.total)
                        if line.salary_rule_id.contrib_sipa or line.contrib_inssjyp or line.contrib_renatea or line.contrib_asignaciones_familiares or line.contrib_fondo_nacional_empleo:
                            base_imp_2_3.append(line.total)
                        if line.salary_rule_id.contrib_obra_social or line.contrib_fsr:
                            base_imp_8.append(line.total)
                        if line.salary_rule_id.contrib_ley_riego_trabajo:
                            base_imp_9.append(line.total)
                        
                        _logger.info('Composición de base_imp_1_5: %s', base_imp_1_5)
                        _logger.info('Composición de base_imp_2_3: %s', base_imp_2_3)
                        _logger.info('Composición de base_imp_4: %s', base_imp_4)
                        _logger.info('Composición de base_imp_8: %s', base_imp_8)
                        _logger.info('Composición de base_imp_9: %s', base_imp_9)

                    if line.salary_rule_id.aporte_regimenes_diferenciales:
                        base_imp_6.append(line.total)

                    if line.salary_rule_id.aporte_regimenes_especiales:
                        base_imp_7.append(line.total)

            payslip.employee_id.base_imponible_1 = sum(base_imp_1_5)
            payslip.employee_id.base_imponible_5 = sum(base_imp_1_5)
            payslip.employee_id.base_imponible_4 = sum(base_imp_4)
            payslip.employee_id.base_imponible_2 = sum(base_imp_2_3)
            payslip.employee_id.base_imponible_3 = sum(base_imp_2_3)
            payslip.employee_id.base_imponible_8 = sum(base_imp_8)
            payslip.employee_id.base_imponible_9 = sum(base_imp_9)

            _logger.info('Totales calculados: neto=%s, haberes_remunerativos=%s, haberes_no_remunerativos=%s, descuentos=%s, basico=%s, remuneracion_bruta=%s',
                         neto, haberes_remunerativos, haberes_no_remunerativos, descuentos, basico, remuneracion_bruta)

            libro_model = self.env['hr.employee.libro']
            libro = libro_model.search(
                [('employe_id', '=', payslip.employee_id.id), ('nro_libro', '=', payslip.payslip_run_id.nro_procesamiento_liquidacion)], limit=1)

            valores = {
                "remuneracion_bruta": remuneracion_bruta,
                "base_imponible_1": sum(base_imp_1_5),
                "base_imponible_5": sum(base_imp_1_5),
                "base_imponible_4": sum(base_imp_4),
                "base_imponible_2": sum(base_imp_2_3),
                "base_imponible_3": sum(base_imp_2_3),
                "base_imponible_8": sum(base_imp_8),
                "base_imponible_9": sum(base_imp_9),
            }

            if libro:
                libro.write(valores)
            else:
                valores.update({
                    "employe_id": payslip.employee_id.id,
                    "nro_libro": payslip.payslip_run_id.nro_procesamiento_liquidacion,
                })
                libro_model.create(valores)

            _logger.info('Valores guardados en hr.employee.libro: %s', valores)

        return True

