from odoo import _, api, fields, models, tools
from datetime import *


class HrPayslipRunInherit(models.Model):
    _inherit = 'hr.payslip.run'
    _description = "Inherit payslip run"

    fecha_de_pago = fields.Date('Fecha de pago')
    lugar_de_pago = fields.Char('Lugar de Pago')
    banco_diario_contable_id = fields.Many2one('account.journal', 'Banco últ. depósito',
                                               domain="[('type', '=', 'bank')]")
    fecha_ult_deposito = fields.Date('Fecha últ. depósito')
    periodo_ult_deposito = fields.Date('Período últ. depósito')
    periodo_mes_anio = fields.Char('Período últ. depósito', compute='_transformar_fecha_periodo')
    tipo_liquidacion = fields.Selection(
        [('mensual', 'Mensual'), ('jornal_1', 'Jornal(1° Quincena)'), ('jornal_2', 'Jornal(2° Quincena)'),
         ('aguinaldo', 'Aguinaldo'), ('vacaciones', 'Vacaciones'),
         ('lic_matrimonio', 'Lic. Matrimonio'), ('anticipo', 'Anticipo'), ('ajuste', 'Ajuste'),
         ('liq_final', 'Liquidación Final')])
    nro_procesamiento_liquidacion = fields.Integer('N° Procesamiento de liquidación')

    @api.model
    def create(self, vals):
        vals['nro_procesamiento_liquidacion'] = self.env['ir.sequence'].next_by_code('hr.payslip.run') or _('New')
        return super(HrPayslipRunInherit, self).create(vals)

    @api.depends('periodo_ult_deposito')
    def _transformar_fecha_periodo(self):
        for rec in self:
            if self.periodo_ult_deposito:
                self.periodo_mes_anio = datetime.strptime(str(self.periodo_ult_deposito), '%Y-%m-%d').strftime('%m/%Y')
            else:
                self.periodo_mes_anio = ''

    def empleados_vacaciones_activas(self):
        from_date = self.date_start
        to_date = self. date_end
        empleados_vacaciones = []
        try:
            domain = [('fecha_desde', '>=', from_date), ('fecha_hasta', '<=', to_date), ('liquidado', '=', False )]
            vacaciones_rango = self.env['detalle.vacacion'].sudo().search(domain)

            for v in vacaciones_rango:
                empleado = v.detalle_vacacion_id.empleado_id
                empleados_vacaciones.append(empleado.id)

        except Exception as error_buscando_empleados:
            print('error buscando empleados', str(error_buscando_empleados))

        return {
            'view_mode': 'form',
            'res_model': 'hr.payslip.employees',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_employee_ids':  empleados_vacaciones},
        }


    def empleados_contratos_activos(self):
        contratos_activos = []
        for rec in self:
            try:
                empleados = self.env['hr.employee'].sudo().search([])

                for empleado in empleados:
                    if empleado.contract_id:
                        if empleado.contract_id.state == 'open':
                            contratos_activos.append(empleado.id)

            except Exception as error_buscando_empleados:
                print('error buscando empleados', str(error_buscando_empleados))

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.payslip.employees',
            'target': 'new',
            'context': {'default_employee_ids': contratos_activos},
        }