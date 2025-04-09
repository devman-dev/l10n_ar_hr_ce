# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Users(models.Model):
    _inherit = "res.users"

    portal_employee = fields.Boolean(
        string='Employee Portal',
        compute_sudo=True,
        compute='_compute_portal_employee',
        help='Check this box if this user is an employee portal user.',
        store=True,
    )

    @api.depends('groups_id')
    def _compute_portal_employee(self):
        for user in self:
            user.portal_employee = user._is_employee_portal()

    def _is_employee_portal(self):
        self.ensure_one()
        return self.has_group('gg_portal_employee.group_portal_employee')
