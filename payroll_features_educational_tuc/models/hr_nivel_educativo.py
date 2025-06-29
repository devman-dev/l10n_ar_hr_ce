from odoo import models, fields

class HrNivelEducativo(models.Model):
    _name = 'hr.nivel.educativo'
    _description = 'Nivel Educativo'

    name = fields.Char(string='Nombre', required=True)
    actualiza_x_indice = fields.Boolean(string='Actualiza por Índice')
    actualiza_x_valor_hora = fields.Boolean(string='Actualiza por Valor Hora')
