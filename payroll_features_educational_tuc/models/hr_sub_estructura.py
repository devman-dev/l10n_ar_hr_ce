from odoo import models, fields


class HrSubEstructura(models.Model):
    _name = 'hr.sub.estructura'
    _description = 'Sub Estructura'

    name = fields.Char(string='Nombre', required=True)
    tipo_estructura_id = fields.Many2one('hr.tipo.estructura', string='Tipo de Estructura', required=True)