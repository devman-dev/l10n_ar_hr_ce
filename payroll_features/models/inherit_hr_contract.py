from odoo import _, api, fields, models, tools
from datetime import date, datetime
from dateutil import relativedelta


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'
    _description = "Inherit Hr Contract"

    dias_de_vacaciones = fields.Integer('Dias de vacaciones')
    cantidad_2 = fields.Integer('Cant dias 2')

    @api.onchange('struct_id')
    def copiar_sueldo(self):
        for rec in self:
            rec.wage = rec.struct_id.sueldo_basico
