# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    project_invoice_plan_line_id = fields.Many2one(
        comodel_name='project.invoice.plan.line',
        string='Invoice plan line',
    )
    project_invoice_plan_id = fields.Many2one(
        comodel_name='project.invoice.plan',
        string='Invoice plan line',
        related='project_invoice_plan_line_id.project_invoice_plan_id',
        readonly=True,
    )
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice',
        related='project_invoice_plan_id.invoice_id',
        readonly=True,
    )

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        res = super()._onchange_employee_id()
        if self.employee_id:
            self.product_id = self.get_employee_timesheet_product(self.employee_id)
        return res

    @api.model
    def create(self, values):
        if not values.get('product_id') and values.get('project_id') and values.get('employee_id'):
            employee = self.env['hr.employee'].search(
                [('id', '=', values.get('employee_id'))], limit=1)
            product = self.get_employee_timesheet_product(employee)
            values['product_id'] = product and product.id or False
        result = super(AccountAnalyticLine, self).create(values)
        return result

    @api.model
    def get_employee_timesheet_product(self, employee):
        timesheet_product = employee.timesheet_product_id
        if timesheet_product:
            return timesheet_product
        raise ValidationError(_(
            "Employee %s should have timesheet product defined"
            ) % (employee.name))