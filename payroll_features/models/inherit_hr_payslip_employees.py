from odoo import _, fields, models
from odoo.exceptions import UserError
from datetime import *


class HrPayslipEmployeesInherit(models.TransientModel):
    _inherit = "hr.payslip.employees"
    _description = "Generate payslips for all selected employees"


    def compute_sheet(self):
        payslips = self.env["hr.payslip"]
        [data] = self.read()
        active_id = self.env.context.get("active_id")
        if active_id:
            [run_data] = (
                self.env["hr.payslip.run"]
                .browse(active_id)
                .read(["date_start", "date_end", "credit_note", "struct_id", "lugar_de_pago", "fecha_de_pago", "banco_diario_contable_id", "fecha_ult_deposito", "periodo_ult_deposito", "tipo_liquidacion"])
            )
        from_date = run_data.get("date_start")
        to_date = run_data.get("date_end")
        struct_id = run_data.get("struct_id")
        lugar_de_pago = run_data.get("lugar_de_pago")
        fecha_de_pago = run_data.get("fecha_de_pago")
        banco_diario_contable_id = run_data.get("banco_diario_contable_id")
        fecha_ult_deposito = run_data.get("fecha_ult_deposito")
        periodo_ult_deposito = run_data.get("periodo_ult_deposito")
        tipo_liquidacion = run_data.get("tipo_liquidacion")
        if not data["employee_ids"]:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        for employee in self.env["hr.employee"].browse(data["employee_ids"]):
            slip_data = self.env["hr.payslip"].get_payslip_vals(
                from_date, to_date, employee.id, contract_id=False, struct_id=struct_id
            )

            res = {
                "employee_id": employee.id,
                "name": slip_data["value"].get("name"),
                "struct_id": slip_data["value"].get("struct_id"),
                "contract_id": slip_data["value"].get("contract_id"),
                "payslip_run_id": active_id,
                "input_line_ids": [
                    (0, 0, x) for x in slip_data["value"].get("input_line_ids")
                ],
                "worked_days_line_ids": [
                    (0, 0, x) for x in slip_data["value"].get("worked_days_line_ids")
                ],
                "date_from": from_date,
                "date_to": to_date,
                "credit_note": run_data.get("credit_note"),
                "company_id": employee.company_id.id,
                "lugar_de_pago": lugar_de_pago,
                "fecha_de_pago": fecha_de_pago,
                "banco_diario_contable_id": banco_diario_contable_id[0],
                "fecha_ult_deposito": fecha_ult_deposito,
                "periodo_ult_deposito": periodo_ult_deposito,
                "tipo_liquidacion": tipo_liquidacion,

            }
            if tipo_liquidacion == 'vacaciones':
                try:
                    dom = [('empleado_id', '=', employee.id)]
                    vacaciones = self.env['vacacion'].sudo().search(dom)
                    for rec in vacaciones:
                        contador = 0
                        for det_vac in rec.detalle_vacaciones_ids:
                            if det_vac.liquidado:
                                pass
                            else:
                                res['date_from'] = det_vac.fecha_desde
                                res['date_to'] = det_vac.fecha_hasta
                                res['dias_vacaciones'] = det_vac.cantidad

                                if employee.tipo_empleado == 'uom':
                                    try:
                                        dom_struct = [('code', '=', 'VACUOM')]
                                        estructura_salarial_id = self.env['hr.payroll.structure'].sudo().search(dom_struct)
                                        print(estructura_salarial_id)
                                        res['struct_id'] = estructura_salarial_id.id
                                    except Exception as error_vacaciones_reglas:
                                        print('error vacaciones reglas', str(error_vacaciones_reglas))

                                if employee.tipo_empleado == 'aec':
                                    try:
                                        dom_struct = [('code', '=', 'VACAEC')]
                                        estructura_salarial_id = self.env['hr.payroll.structure'].sudo().search(dom_struct)
                                        print(estructura_salarial_id)
                                        res['struct_id'] = estructura_salarial_id.id
                                    except Exception as error_vacaciones_reglas:
                                        print('error vacaciones reglas', str(error_vacaciones_reglas))

                                if employee.tipo_empleado == 'director':
                                    try:
                                        dom_struct = [('code', '=', 'VACDIR')]
                                        estructura_salarial_id = self.env['hr.payroll.structure'].sudo().search(dom_struct)
                                        print(estructura_salarial_id)
                                        res['struct_id'] = estructura_salarial_id.id
                                    except Exception as error_vacaciones_reglas:
                                        print('error vacaciones reglas', str(error_vacaciones_reglas))

                                if employee.tipo_empleado == 'fuera_convenio':
                                    try:
                                        dom_struct = [('code', '=', 'VACFCON')]
                                        estructura_salarial_id = self.env['hr.payroll.structure'].sudo().search(dom_struct)
                                        print(estructura_salarial_id)
                                        res['struct_id'] = estructura_salarial_id.id
                                    except Exception as error_vacaciones_reglas:
                                        print('error vacaciones reglas', str(error_vacaciones_reglas))

                                payslips = self.env["hr.payslip"].create(res)
                                payslips._compute_name()
                                payslips.compute_sheet()
                                employee.contract_ids.dias_de_vacaciones = 0
                                employee.contract_ids.cantidad_2 = 0
                                contador += 1
                                det_vac.liquidado = True

                except Exception as error_fecha_vacaciones:
                    print('error fecha vacaciones', str(error_fecha_vacaciones))
            else:
                mes_vacacion = ''
                try:
                    domain = [('fecha_desde', '>=', from_date), ('fecha_hasta', '<=', to_date), ('empleado_id', '=', employee.id), ('liquidado', '=', True)]
                    mes_vacacion = self.env['detalle.vacacion'].sudo().search(domain)
                    dias_vacaciones = 0
                    for detalle_vacaciones in mes_vacacion:
                        dias_vacaciones += detalle_vacaciones.cantidad

                    res['dias_vacaciones'] = dias_vacaciones
                except Exception as error_mes_vacaciones:
                    print('Error buscando mes con vacaciones')

                if mes_vacacion:
                    res['mes_vacacion'] = True

                    payslips += self.env["hr.payslip"].create(res)
                    payslips._compute_name()
                    payslips.compute_sheet()
                else:
                    payslips += self.env["hr.payslip"].create(res)
                    payslips._compute_name()
                    payslips.compute_sheet()

        return {"type": "ir.actions.act_window_close"}

