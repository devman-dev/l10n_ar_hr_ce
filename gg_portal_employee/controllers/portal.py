# -*- coding: utf-8 -*-

import base64

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessDenied
from odoo.http import content_disposition, request, route
from odoo import _, tools
from pydantic import BaseModel, ConfigDict
from typing import Optional
from werkzeug.datastructures import FileStorage
from datetime import datetime


class LegajoPortalUpdateDTO(BaseModel):
    model_config = ConfigDict(extra='ignore')

    marital: Optional[str] = None
    private_email: Optional[str] = None
    private_phone: Optional[str] = None
    private_street: Optional[str] = None
    private_city: Optional[str] = None
    private_zip: Optional[str] = None
    children: Optional[str] = None
    account_number: Optional[str] = None
    bank_id: Optional[str] = None

class AusenciasPortalDTO(BaseModel):
    model_config = ConfigDict(extra='ignore', arbitrary_types_allowed=True)
    hr_leave_type: str
    date_start: str
    date_end: str
    description: Optional[str] = None
    attachment: Optional[FileStorage] = None

class EmployeePortal(CustomerPortal):

    @route(['/my/payslips'], type='http', auth='user', website=True)
    def payrolls(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        values.update({
            'error': {},
            'error_message': [],
        })

        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        payslips = request.env['hr.payslip'].sudo().search([('employee_id', '=', employee.id), ('state', 'in', ['done', 'paid'])], order='date_from desc')

        values.update({
            'employee': employee,
            'payslips': payslips,
            'redirect': redirect,
            'page_name': 'my_payslips',
        })

        response = request.render("gg_portal_employee.portal_my_payslips", values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    @route(['/my/legajo'], type='http', auth='user', website=True)
    def legajo(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        values.update({
            'error': {},
            'error_message': [],
        })
        marital_status_mapper = {
            'Soltero/a': 'single',
            'Casado/a': 'married',
            'Divorciado/a': 'divorced',
            'Viudo/a': 'widower',
            'Concubino/a': 'legal_cohabitant',
        }

        if post and request.httprequest.method == 'POST':
            error = dict()
            error_message = []
            data = LegajoPortalUpdateDTO(**post)
            employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
            bank_account = employee.bank_account_id
            # email validation
            if data.private_email and not tools.single_email_re.match(data.private_email):
                error["private_email"] = 'error'
                error_message.append(_('Invalid Email! Please enter a valid email address.'))
            if data.children and not data.children.isdigit():
                error["children"] = 'error'
                error_message.append(_('Invalid Children! Please enter a valid number of children.'))
            if data.marital not in marital_status_mapper.keys():
                error["marital"] = 'error'
                error_message.append(_('Invalid Marital Status! Please select a valid marital status.'))
            if data.private_zip and not data.private_zip.isdigit():
                error["zip"] = 'error'
                error_message.append(_('Invalid ZIP Code! Please enter a valid ZIP code.'))
            if data.private_city and data.private_city == '':
                error["private_city"] = 'error'
                error_message.append(_('Invalid City! Please enter a valid city.'))
            if data.private_street and data.private_street == '':
                error["private_street"] = 'error'
                error_message.append(_('Invalid Street! Please enter a valid street.'))
            if data.private_phone and not data.private_phone.isdigit():
                error["private_phone"] = 'error'
                error_message.append(_('Invalid Phone! Please enter a valid phone number.'))
            if data.account_number and not data.account_number.isdigit():
                error["account_number"] = 'error'
                error_message.append(_('Invalid Account Number! Please enter a valid account number.'))
            if data.bank_id and not data.bank_id.isdigit():
                error["bank_id"] = 'error'
                error_message.append(_('Invalid Bank! Please select a valid bank.'))
            elif data.bank_id and not request.env['res.bank'].sudo().browse(int(data.bank_id)).exists():
                error["bank_id"] = 'error'
                error_message.append(_('Invalid Bank! Please select a valid bank.'))
            if not data.bank_id or not data.account_number:
                error["bank_id"] = 'error'
                error["account_number"] = 'error'
                error_message.append(_('Bank and Account Number are required fields! Please fill them in.'))
            if error:
                values.update({
                    'error': error,
                    'error_message': error_message,
                })
            else:
                if bank_account:
                    bank_account.sudo().write({
                        'acc_number': data.account_number,
                        'bank_id': int(data.bank_id),
                    })
                else:
                    bank_account = request.env['res.partner.bank'].sudo().create({
                        'acc_number': data.account_number,
                        'bank_id': int(data.bank_id),
                        'acc_holder_name': employee.name,
                        'partner_id': employee.user_partner_id.id,
                        'currency_id': employee.company_id.currency_id.id,
                    })
                data_to_update = data.model_dump(exclude_none=True, exclude={'account_number', 'bank_id'})
                if data.marital:
                    data_to_update['marital'] = marital_status_mapper[data.marital]
                if data.children:
                    data_to_update['children'] = int(data.children)
                data_to_update['bank_account_id'] = bank_account.id
                employee.sudo().write(
                    data_to_update
                )

                values.update({
                    'success_message': _('Your data has been updated successfully!'),
                })


        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        bancos = request.env['res.bank'].sudo().search([])
        values.update({
            'employee': employee,
            'bancos': bancos,
            'redirect': redirect,
            'page_name': 'my_payslips',
        })

        response = request.render("gg_portal_employee.portal_my_legajo", values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    @route(['/my/permits'], type='http', auth='user', website=True)
    def permits(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            error = dict()
            error_message = []
            data = AusenciasPortalDTO(**post)
            if not data.hr_leave_type or not data.hr_leave_type.isdigit():
                error["hr_leave_type"] = 'error'
                error_message.append(_('Invalid Leave Type! Please select a valid leave type.'))
            elif not request.env['hr.leave.type'].sudo().browse(int(data.hr_leave_type)):
                error["hr_leave_type"] = 'error'
                error_message.append(_('Leave type not found! Please select a valid leave type.'))
            if not data.date_start:
                error["date_start"] = 'error'
                error_message.append(_('Invalid Start Date! Please enter a valid start date.'))
            if not data.date_end:
                error["date_end"] = 'error'
                error_message.append(_('Invalid End Date! Please enter a valid end date.'))
            employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
            if not employee:
                error_message.append(_('Employee not found! Please contact your HR department.'))
            leave_type = request.env['hr.leave.type'].sudo().browse(int(data.hr_leave_type))
            if not leave_type:
                error_message.append(_('Leave type not found! Please contact your HR department.'))
            attachment_data = data.attachment.stream.read() if data.attachment else None
            try:
                date_from = datetime.strptime(data.date_start, '%Y-%m-%d')
                date_to = datetime.strptime(data.date_end, '%Y-%m-%d')
            except ValueError:
                error["date_start"] = 'error'
                error["date_end"] = 'error'
                error_message.append(_('Invalid Dates! Please enter valid dates.'))

            if error:
                values.update({
                    'error': error,
                    'error_message': error_message,
                })
            else:
                leave = request.env['hr.leave'].sudo().create({
                    'holiday_status_id': leave_type.id,
                    'employee_id': employee.id,
                    'request_date_from': date_from,
                    'request_date_to': date_to,
                    'name': data.description,
                })
                if attachment_data and data.attachment:
                    request.env['ir.attachment'].sudo().create({
                        'res_model': 'hr.leave',
                        'res_id': leave.id,
                        'name': data.attachment.filename,
                        'datas': base64.b64encode(attachment_data),
                        'type': 'binary',
                        'mimetype': 'application/pdf',
                    })

                values.update({
                    'success_message': _('Your request has been submitted successfully!'),
                })

        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        hr_leave_types = request.env['hr.leave.type'].sudo().search([])
        values.update({
            'employee': employee,
            'hr_leave_types': hr_leave_types,
            'redirect': redirect,
            'page_name': 'my_permits',
        })

        response = request.render("gg_portal_employee.portal_my_permits", values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    @route(['/my/payslip/download/<int:payslip_id>'], type='http', auth='user', website=True)
    def download_payslip(self, payslip_id, **kw):
        Payslip = request.env['hr.payslip'].sudo()
        payslip = Payslip.browse(payslip_id)

        if not payslip.exists():
            return request.not_found()

        if payslip.employee_id.user_id.id != request.env.user.id:
            raise AccessDenied()

        # Generar el PDF desde el action report
        pdf = request.env.ref('payroll.action_report_payslip').sudo().report_action(None,data=payslip)

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', content_disposition(f"Payslip - {payslip.employee_id.name}.pdf"))
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

    def _prepare_portal_layout_values(self):
        """Values for /my/* templates rendering.

        Does not include the record counts.
        """
        values = super(EmployeePortal, self)._prepare_portal_layout_values()

        return values | {
            'is_employee_portal': request.env.user._is_employee_portal(),
        }
