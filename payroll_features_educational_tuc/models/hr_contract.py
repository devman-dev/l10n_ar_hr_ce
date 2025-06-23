from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    decreto_413 = fields.Boolean(string='Contiene Decreto 413/3', default=False)
    decreto_1741 = fields.Boolean(string='Contiene Decreto 1741/3 Art. 1', default=False)
    decreto_2780 = fields.Boolean(string='Contiene Decreto 2780/3 Art. 10', default=False)
    
    nivel_educativo = fields.Selection([
        ('inicial', 'Inicial'),
        ('primario', 'Primario'),
        ('secundario', 'Secundario'),
        ('terciario', 'Terciario'),
        ('universitario', 'Universitario'),
    ], string='Nivel Educativo', required=True)

    antiguedad_fecha = fields.Date('Fecha de Antigüedad')

    # 🔧 Sobrescribimos el create para evitar la validación del contrato único
    @api.model
    def create(self, vals):
        # Desactivar validación de contrato único por empleado
        self = self.with_context(skip_contract_check=True)
        return super(HrContractInherit, self).create(vals)

    def write(self, vals):
        # Igual para actualización
        self = self.with_context(skip_contract_check=True)
        return super(HrContractInherit, self).write(vals)

    # 🧨 Sobreescribimos la validación original para que respete el contexto
    @api.constrains('employee_id', 'state')
    def _check_contracts(self):
        if self.env.context.get('skip_contract_check'):
            return  # ⚠️ Anulamos si venimos desde nuestro override
        for contract in self:
            if contract.state not in ['draft', 'cancel'] and contract.employee_id:
                domain = [
                    ('employee_id', '=', contract.employee_id.id),
                    ('state', 'not in', ['draft', 'cancel']),
                    ('id', '!=', contract.id),
                ]
                other_contracts = self.env['hr.contract'].search(domain, limit=1)
                if other_contracts:
                    raise ValidationError(
                        "Un empleado solo puede tener un contrato activo a la vez (por defecto de Odoo)."
                    )
    
    # Sobrescribimos la restricción para permitir varios contratos activos con distinto nivel educativo
    @api.constrains('employee_id', 'state', 'nivel_educativo')
    def _check_multiple_contracts_per_nivel(self):
        for contract in self:
            if contract.state not in ('draft', 'cancel'):
                domain = [
                    ('employee_id', '=', contract.employee_id.id),
                    ('state', 'not in', ('draft', 'cancel')),
                    ('nivel_educativo', '=', contract.nivel_educativo),
                    ('id', '!=', contract.id)
                ]
                other = self.search_count(domain)
                if other:
                    raise models.ValidationError(
                        "Un empleado solo puede tener un contrato activo por nivel educativo a la vez."
                    )
