from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    indice_educativo = fields.Float(string="Índice Educativo", digits=(16, 8))

    def write(self, vals):
        res = super().write(vals)
        if 'indice_educativo' in vals:
            self.env['hr.payroll.structure'].search([]).update_indice_and_basic(self.indice_educativo)
        return res
