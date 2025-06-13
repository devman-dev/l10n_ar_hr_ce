from odoo import models, fields

class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    decreto_413 = fields.Boolean(string='Contiene Decreto 413/3', default=False)
