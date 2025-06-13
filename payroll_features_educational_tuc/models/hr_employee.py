from odoo import models, fields

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    sublegajo = fields.Integer('Sublegajo')
