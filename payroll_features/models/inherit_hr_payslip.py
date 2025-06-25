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

    # Nuevos campos para el SAC
    x_sac_mejor_remuneracion_base = fields.Float(string='SAC: Mejor Remuneración Base', readonly=True, copy=False)
    x_sac_dias_proporcionales = fields.Integer(string='SAC: Días Proporcionales', readonly=True, copy=False)

    @api.model
    def create(self, vals):
        vals['nro_recibo'] = self.env['ir.sequence'].next_by_code('hr.payslip') or _('New')
        return super(HrPayslipInherit, self).create(vals)

    @api.depends('fecha_de_pago')
    def _calcular_totales(self):
        if self.dynamic_filtered_payslip_lines:
            for rec in self.dynamic_filtered_payslip_lines:
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
        # Limpiar los campos x_sac_* al inicio del cálculo por si acaso
        for payslip in self:
            payslip.x_sac_mejor_remuneracion_base = 0.0
            payslip.x_sac_dias_proporcionales = 0

        # El super().compute_sheet() llamará a la lógica de Odoo Payroll que a su vez
        # llamará a self.get_payslip_lines() (que es _get_lines_dict en este módulo heredado)
        # para cada regla.
        # La regla SAC_CALCULADO poblará los campos x_sac_* en el objeto 'payslip' en memoria.
        original_compute_sheet_result = super(HrPayslipInherit, self).compute_sheet()

        # Después de que todas las líneas han sido calculadas (incluida la del SAC),
        # y los campos x_sac_* han sido poblados por la regla del SAC,
        # la lógica de `payroll_features` para `compute_sheet` (la que estamos heredando y sobreescribiendo)
        # se ejecutará. Esa lógica ya recalcula los totales (neto, haberes_remunerativos, etc.)
        # y las bases imponibles, y finalmente hace un `payslip.write`.

        # La lógica original de compute_sheet en este módulo payroll_features es extensa.
        # Lo crucial es que nuestros campos x_sac_* sean poblados *antes* de que esa lógica
        # haga sus cálculos finales y el `write`.
        # El `super(HrPayslipInherit, self).compute_sheet()` que está arriba ya invoca la lógica
        # que procesa las reglas salariales. Dentro de la regla del SAC (específicamente en su código Python),
        # se deben asignar los valores a `localdict['payslip'].x_sac_mejor_remuneracion_base` y
        # `localdict['payslip'].x_sac_dias_proporcionales`.

        # La función compute_sheet de este mismo módulo (payroll_features) que estamos modificando
        # ya contiene la lógica para:
        # 1. Llamar a get_lines_dict (que procesa las reglas).
        # 2. Calcular los totales (neto, haberes_remunerativos, etc.) basados en los códigos de las líneas.
        # 3. Calcular las bases imponibles (base_imponible_1, base_imponible_2, etc.).
        # 4. Escribir todos estos valores en el payslip.
        # 5. Actualizar/crear el registro en hr.employee.libro.

        # Por lo tanto, no necesitamos replicar toda esa lógica aquí.
        # Solo necesitamos asegurar que la llamada a `super().compute_sheet()` ocurra
        # y que nuestra regla del SAC haga su trabajo.
        # La inicialización de los campos x_sac_* ya se hizo al principio.

        # El siguiente código es para recalcular los totales después de que todas las líneas, incluida la del SAC,
        # se hayan procesado por el `super().compute_sheet()` y la lógica de `get_lines_dict`.
        # Esto asegura que los campos como `neto`, `haberes_remunerativos` reflejen la inclusión del SAC.
        for payslip_rec in self:
            total_en_texto = ''
            haberes_remunerativos = 0.0
            haberes_no_remunerativos = 0.0
            descuentos = 0.0
            basico = 0.0
            neto = 0.0
            remuneracion_bruta_calc = 0.0

            for line in payslip_rec.line_ids:
                if line.code == 'C_1000': # NETO
                    neto = line.total
                    pre = round(float(neto), 2)
                    entire_num_str, decimal_num_str = str(pre).split('.') if '.' in str(pre) else (str(pre), '0')
                    entire_num = int(entire_num_str)
                    decimal_num = int(decimal_num_str)
                    if len(decimal_num_str) == 1: # ej .1 -> 10 centavos
                        decimal_num *= 10
                    elif len(decimal_num_str) == 0: # ej. no decimal part
                         decimal_num = 0

                    text_parts = [num2words(entire_num, lang='es') if entire_num > 0 else "cero"]
                    text_parts.append(' con ')
                    text_parts.append(num2words(decimal_num, lang='es') if decimal_num > 0 else "cero")
                    total_en_texto = "".join(text_parts).upper()

                elif line.code == 'C_1001': # HABERES REMUNERATIVOS
                    haberes_remunerativos = line.total
                elif line.code == 'C_1002': # HABERES NO REMUNERATIVOS
                    haberes_no_remunerativos = line.total
                elif line.code == 'C_1003': # DESCUENTOS
                    descuentos = line.total
                elif line.code == 'C1': # BASICO (asumiendo C1 es el básico)
                    basico = line.total
                elif line.code == 'C_1004': # REMUNERACION BRUTA TOTAL
                    remuneracion_bruta_calc = line.total

            # Estos valores se escribirán por el `write` que está al final de la función
            # compute_sheet original de payroll_features. No necesitamos un write aquí.
            payslip_rec.neto = round(neto, 2)
            payslip_rec.total_en_texto = total_en_texto
            payslip_rec.haberes_remunerativos = round(haberes_remunerativos, 2)
            payslip_rec.haberes_no_remunerativos = round(haberes_no_remunerativos, 2)
            payslip_rec.descuentos = round(descuentos, 2)
            payslip_rec.basico = round(basico, 2)
            payslip_rec.remuneracion_bruta = round(remuneracion_bruta_calc, 2)
            if payslip_rec.employee_id and hasattr(payslip_rec.employee_id, 'remuneracion_bruta'):
                 payslip_rec.employee_id.remuneracion_bruta = round(remuneracion_bruta_calc, 2)


        # La lógica de cálculo de bases imponibles y actualización de hr.employee.libro
        # ya está en la parte de la función compute_sheet de payroll_features que se ejecuta
        # después de que las líneas son generadas por get_lines_dict.
        # El `original_compute_sheet_result` ya contiene el `True` o lo que devuelva la función original.
        return original_compute_sheet_result

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
            # La siguiente línea fue modificada para asegurar que el objeto completo `rule` esté disponible si es necesario
            # en lugar de solo un BaseBrowsableObject con los valores. Esto puede no ser necesario para el SAC.
            # localdict["result_rules"].dict[rule.code] = BaseBrowsableObject(values)
            localdict["result_rules"].dict[rule.code] = rule # O mantener el BaseBrowsableObject si es suficiente

        localdict = self._sum_salary_rule_category(
            localdict, rule.category_id, total - previous_amount
        )

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
        if category.code: # Asegurarse de que la categoría tiene un código antes de intentar acceder a él
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
                        # La lógica original tenía un error aquí, accedía a campos como line.aporte_inssjyp que no existen en hr.payslip.line
                        # Debe ser line.salary_rule_id.aporte_inssjyp
                        rule_of_line = line.salary_rule_id
                        if rule_of_line:
                            if rule_of_line.aporte_sipa or rule_of_line.aporte_inssjyp:
                                base_imp_1_5.append(line.total)
                            if rule_of_line.aporte_obra_social or rule_of_line.aporte_fsr:
                                base_imp_4.append(line.total)
                            if rule_of_line.contrib_sipa or rule_of_line.contrib_inssjyp or rule_of_line.contrib_renatea or rule_of_line.contrib_asignaciones_familiares or rule_of_line.contrib_fondo_nacional_empleo:
                                base_imp_2_3.append(line.total)
                            if rule_of_line.contrib_obra_social or rule_of_line.contrib_fsr:
                                base_imp_8.append(line.total)
                            if rule_of_line.contrib_ley_riego_trabajo:
                                base_imp_9.append(line.total)
                        
                        _logger.info('Composición de base_imp_1_5: %s', base_imp_1_5)
                        _logger.info('Composición de base_imp_2_3: %s', base_imp_2_3)
                        _logger.info('Composición de base_imp_4: %s', base_imp_4)
                        _logger.info('Composición de base_imp_8: %s', base_imp_8)
                        _logger.info('Composición de base_imp_9: %s', base_imp_9)

                    rule_of_line = line.salary_rule_id
                    if rule_of_line:
                        if rule_of_line.aporte_regimenes_diferenciales:
                            base_imp_6.append(line.total)

                        if rule_of_line.aporte_regimenes_especiales:
                            base_imp_7.append(line.total)

            if payslip.employee_id: # Verificar que el empleado exista
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
            # Asegurarse de que nro_procesamiento_liquidacion no sea None
            nro_libro_search = payslip.payslip_run_id.nro_procesamiento_liquidacion if payslip.payslip_run_id else None

            libro = None
            if payslip.employee_id and nro_libro_search: # Solo buscar si hay empleado y nro_libro
                libro = libro_model.search(
                    [('employe_id', '=', payslip.employee_id.id), ('nro_libro', '=', nro_libro_search)], limit=1)

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

            if libro: # Si se encontró un libro
                libro.write(valores)
            elif payslip.employee_id and nro_libro_search: # Solo crear si hay empleado y nro_libro y no se encontró antes
                valores.update({
                    "employe_id": payslip.employee_id.id,
                    "nro_libro": nro_libro_search,
                })
                libro_model.create(valores)

            _logger.info('Valores guardados en hr.employee.libro: %s', valores)

        return True

