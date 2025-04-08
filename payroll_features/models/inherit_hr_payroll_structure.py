from odoo import _, api, fields, models, tools
from datetime import *

class HrPayrollStrucureInherit(models.Model):
    _inherit = 'hr.payroll.structure'
    _description = "Inherit Hr Payroll Structure"

    sueldo_basico = fields.Float('Sueldo Básico')
    retrib_categ_ids = fields.One2many('retribuciones.categorias', 'retrib_categ_id')

    @api.constrains('sueldo_basico')
    def actualizar_sueldos(self):
        for rec in self:
            try:
                domain = [('struct_id', '=', self.ids[0])]
                contrato = self.env['hr.contract'].sudo().search(domain)
                for c in contrato:
                    c.wage = rec.sueldo_basico
                    c.contract_wage = rec.sueldo_basico

                self.write({'retrib_categ_ids': [(0, 0, {'retribucion': rec.sueldo_basico,
                                                         'vigencia_desde': datetime.now(),
                                                         })]})
            except Exception as error_actualizando_sueldos:
                print('Error actualizando sueldos', str(error_actualizando_sueldos))


class RetribucionesCategorias(models.Model):
    _name = 'retribuciones.categorias'
    _description = 'Modelo para almacenar las reribuciones anteriores'

    retribucion = fields.Float('Retribución')
    vigencia_desde = fields.Date('Vigencia desde')
    retrib_categ_id = fields.Many2one('hr.payroll.structure')
