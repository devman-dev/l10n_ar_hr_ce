from odoo.http import request


def is_user_internal(uid):
    return request.env['res.users'].browse(uid)._is_internal()
