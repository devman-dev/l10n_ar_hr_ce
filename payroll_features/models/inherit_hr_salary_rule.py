from odoo import _, api, fields, models, tools


class HrSalaryRuleInherit(models.Model):
    _inherit = 'hr.salary.rule'
    _description = "Inherit Hr Salary Rule"

    marca_repeticion = fields.Boolean('Repetible')

    aporte_sipa = fields.Boolean('Aporte SIPA')
    contrib_sipa = fields.Boolean('Contribución SIPA')

    aporte_inssjyp = fields.Boolean('Aporte INSSJyP')
    contrib_inssjyp = fields.Boolean('Contribución INSSJyP')

    aporte_obra_social = fields.Boolean('Aporte Obra social')
    contrib_obra_social = fields.Boolean('Contribución Obra social')

    aporte_fsr = fields.Boolean('Aporte FSR (Ex ANSSAL)')
    contrib_fsr = fields.Boolean('Contribución FSR (Ex ANSSAL)')

    aporte_renatea = fields.Boolean('Aporte RENATEA (Ex RENATRE)')
    contrib_renatea = fields.Boolean('Contribución RENATEA (Ex RENATRE)')

    # aporte_asignaciones_familiares = fields.Boolean('Aporte Asig. Familiares (AAFF)', default=False, readonly=True)
    contrib_asignaciones_familiares = fields.Boolean('Contribución Asig. Familiares (AAFF)')

    # aporte_fondo_nacional_empleo = fields.Boolean('Aporte Fondo Nacional de empleo (FNE)', default=False, readonly=True)
    contrib_fondo_nacional_empleo = fields.Boolean('Contribución Fondo Nacional de empleo (FNE)')

    # aporte_ley_riesgo_trabajo = fields.Boolean('Aporte Ley de Riesgos del Trabajo (LRT)', default=False, readonly=True)
    contrib_ley_riego_trabajo = fields.Boolean('Contribución Ley de Riesgos del Trabajo (LRT)')

    aporte_regimenes_diferenciales = fields.Boolean('Aporte Regímenes Diferenciales')
    # contrib_regimenes_difrenciales = fields.Boolean('Contribución Regímenes Diferenciales', default=False,
    #                                                 readonly=True)
    aporte_regimenes_especiales = fields.Boolean('Aporte Regímenes Especiales')
    # contrib_regimenes_especiales = fields.Boolean('Contribución Regímenes Especiales', default=False,
    #                                               readonly=True)
    custom_amount_ids = fields.One2many('hr.salary.rule.custom.amount', 'custom_amount_id')

    custom_amount = fields.Boolean('Importe manual')

    custom_aux_rule = fields.Boolean('Regla de calculo auxiliar')


    @api.onchange('custom_amount_ids')
    def check_rules(self):
        empleados = self.env['hr.employee'].sudo().search([])
        for emp in empleados:
            if self.name == 'A cuenta futuros':
                emp.regla_a_cuenta_futuros = False

        for rec in self.custom_amount_ids:
            if self.name == 'A cuenta futuros':
                rec.employee_id.regla_a_cuenta_futuros = True

        for rec in self.custom_amount_ids:
            if rec.employee_id.contract_id.struct_id:
                rec.categoria = rec.employee_id.contract_id.struct_id.display_name


class HrSalaryRuleCustomAmount(models.Model):
    _name = 'hr.salary.rule.custom.amount'
    _description = "Inherit Hr Salary Rule Perzonalized Concept"

    employee_id = fields.Many2one('hr.employee')
    categoria = fields.Char('Categoría')
    importe = fields.Float('Importe')
    custom_amount_id = fields.Many2one('hr.salary.rule')



