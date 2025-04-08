from odoo import fields, models


class ExtendsResCompany(models.Model):
	_inherit = 'res.company'


	signature = fields.Image('Firma')