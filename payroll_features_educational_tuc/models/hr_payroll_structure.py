from odoo import models, fields, api

class HrPayrollStructure(models.Model):
    _inherit = "hr.payroll.structure"

    puntos = fields.Float(string="Puntos")
    indice = fields.Float(string="Índice", digits=(16, 8))

    tipo_estructura = fields.Selection([
        ('docente', 'Docente'),
        ('no_docente', 'No Docente')
    ], string='Tipo de Estructura')

    sub_estructura = fields.Selection([
        ('administrativo', 'Administrativo'),
        ('jerarquico', 'Jerárquico')
    ], string='Sub-estructura')

    @api.onchange('puntos', 'indice')
    def _onchange_puntos_indice(self):
        if self.puntos and self.indice:
            self.sueldo_basico = self.puntos * self.indice

    def update_indice_and_basic(self, new_indice):
        for structure in self:
            structure.write({
                'indice': new_indice,
                'sueldo_basico': structure.puntos * new_indice
            })
