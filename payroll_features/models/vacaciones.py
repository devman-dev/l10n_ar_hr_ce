from odoo import _, api, fields, models, tools

from datetime import date, datetime
from dateutil import relativedelta
from odoo.exceptions import ValidationError


class Vacaciones(models.Model):
    _name = 'vacacion'
    _description = "Modelo para vacaciones"


    anio = fields.Integer('Año')
    empleado_id = fields.Many2one('hr.employee', string="Empleado")
    fecha_alta = fields.Date('Fecha de alta')
    dias_de_vacaciones = fields.Integer('Días de Vacaciones')
    detalle_vacaciones_ids = fields.One2many('detalle.vacacion', 'detalle_vacacion_id')


    @api.onchange('empleado_id')
    def _extraer_fecha_de_alta(self):
        for rec in self:
            if rec.empleado_id.contract_id:
                rec.fecha_alta = rec.empleado_id.contract_id.date_start

                tiempo_transc = ''

                fecha_inicial = rec.fecha_alta
                fecha_fin = datetime.now()
                tiempo_transc = relativedelta.relativedelta(fecha_fin, fecha_inicial)

                if tiempo_transc.years < 5:
                    self.dias_de_vacaciones = 14
                if 5 <= tiempo_transc.years < 10:
                    self.dias_de_vacaciones = 21
                if 10 <= tiempo_transc.years < 20:
                    self.dias_de_vacaciones = 28
                if tiempo_transc.years > 20:
                    self.dias_de_vacaciones = 35
            else:
                rec.fecha_alta = ''

    @api.onchange('detalle_vacaciones_ids')
    def limitar_registros(self):
        cantidad_dias_vacaciones = []
        for rec in self:
            if rec.detalle_vacaciones_ids:
                for reg in rec.detalle_vacaciones_ids:
                    cantidad_dias_vacaciones.append(reg.cantidad)
            total_dias = sum(cantidad_dias_vacaciones)
            if total_dias > self.dias_de_vacaciones:
                raise ValidationError('No se puede agregar mas dias de vacaciones')


class DetalleVcaciones(models.Model):
    _name = 'detalle.vacacion'
    _description = 'Detalle de Vacaciones'

    fecha_desde = fields.Date('Fecha desde')
    fecha_hasta = fields.Date('Fecha hasta')
    cantidad = fields.Integer('Cantidad')
    cantidad_antiguedad = fields.Integer('Cantidad antiguedad')
    detalle_vacacion_id = fields.Many2one('vacacion')
    liquidado = fields.Boolean('Liquidado')
    empleado_id = fields.Many2one('hr.employee', string="Empleado")

    @api.onchange('fecha_desde', 'fecha_hasta')
    def calc_dias_vacaciones(self):
        for rec in self:
            if rec.fecha_desde and rec.fecha_hasta:
                fecha_inicial = rec.fecha_desde
                fecha_fin = rec.fecha_hasta
                # tiempo_transc = relativedelta.relativedelta(fecha_fin, fecha_inicial)
                tiempo_transc = (fecha_fin - fecha_inicial).days + 1
                rec.cantidad = tiempo_transc

                if rec.cantidad > rec.cantidad_antiguedad:
                    raise ValidationError(
                        'La cantidad de dias de vacaciones es mayor a la cantidad de dias otorgados por la antiguedad')
            else:
                pass
