from odoo import models, fields

class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    decreto_413 = fields.Boolean(string='Contiene Decreto 413/3', default=False)
    decreto_1741 = fields.Boolean(string='Contiene Decreto 1741/3 Art. 1', default=False)
    decreto_2780 = fields.Boolean(string='Contiene Decreto 2780/3 Art. 10', default=False)
