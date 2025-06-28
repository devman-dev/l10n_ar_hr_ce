from odoo import models, fields

class HrNivelEducativo(models.Model):
    _name = 'hr.nivel.educativo'
    _description = 'Nivel Educativo'

    name = fields.Char(string='Nombre', required=True)
    actualiza_x_indice = fields.Boolean(string='Actualiza por Índice')
    actualiza_x_valor_hora = fields.Boolean(string='Actualiza por Valor Hora')


# filepath: /opt/odoo17/extra-addons/l10n_ar_hr_ce/payroll_features_educational_tuc/models/hr_tipo_estructura.py
from odoo import models, fields

class HrTipoEstructura(models.Model):
    _name = 'hr.tipo.estructura'
    _description = 'Tipo de Estructura'

    name = fields.Char(string='Nombre', required=True)


# filepath: /opt/odoo17/extra-addons/l10n_ar_hr_ce/payroll_features_educational_tuc/models/hr_sub_estructura.py
from odoo import models, fields

class HrSubEstructura(models.Model):
    _name = 'hr.sub.estructura'
    _description = 'Sub Estructura'

    name = fields.Char(string='Nombre', required=True)
    tipo_estructura_id = fields.Many2one('hr.tipo.estructura', string='Tipo de Estructura', required=True)