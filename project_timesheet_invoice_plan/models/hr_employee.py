# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    timesheet_product_id = fields.Many2one(
        comodel_name='product.product',
        string="Timesheet product",
        domain=[('type', '=', 'service')]
    )
