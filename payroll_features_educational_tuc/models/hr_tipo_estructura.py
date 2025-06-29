from odoo import models, fields

class HrTipoEstructura(models.Model):
    _name = 'hr.tipo.estructura'
    _description = 'Tipo de Estructura'

    name = fields.Char(string='Nombre', required=True)