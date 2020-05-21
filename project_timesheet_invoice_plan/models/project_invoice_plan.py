# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class ProjectInvoicePlan(models.Model):
    _name = 'project.invoice.plan'
    _description = 'Invoice plan from Project'
    _order = 'invoice_date desc'

    name = fields.Char(
        string='Name'
    )
    invoice_date = fields.Date(
        string='Invoice Date'
    )
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice'
    )
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project'
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company'
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner'
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency'
    )
    project_invoice_plan_line_ids = fields.One2many(
        comodel_name='project.invoice.plan.line',
        inverse_name='project_invoice_plan_id',
        string='Lines'
    )
    description = fields.Text(
        string='Description'
    )
    note = fields.Text(
        string='Note'
    )

    @api.multi
    def invoice_create(self):
        invoice_ids = []
        invoice_obj = self.env['account.invoice']
        invoice_line_obj = self.env['account.invoice.line']

        invoice_vals = self._prepare_invoice()
        invoice = invoice_obj.create(invoice_vals)

        for line in self.project_invoice_plan_line_ids:
            line_vals = self._prepare_invoice_line(line)
            if line_vals:
                line_vals.update({'invoice_id': invoice.id})
                invoice_line = invoice_line_obj.create(line_vals)
        invoice_ids.append(invoice.id)
        if invoice:
            self.write({'invoice_id': invoice.id})
        return invoice_ids

    @api.multi
    def _prepare_invoice(self):
        company_id = self.env['res.company']._company_default_get('project.invoice.plan')
        company = self.company_id or company_id
        invoice_vals = {
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'company_id': company.id,
        }
        return invoice_vals

    @api.multi
    def _prepare_invoice_line(self, line):

        product = line.product_id.with_context(force_company=self.company_id.id)
        account = product.property_account_income_id or product.categ_id.property_account_income_categ_id

        if not account and line.product_id:
            raise UserError(_(
                'Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                            (line.product_id.name, line.product_id.id,
                             line.product_id.categ_id.name))

        fpos = line.project_invoice_plan_id.partner_id.property_account_position_id
        if fpos and account:
            account = fpos.map_account(account)

        code = line.product_id.default_code
        name = line.product_id.name
        if code:
            name = '[' + line.product_id.default_code + ']' + line.product_id.name
        line_vals = {
            'product_id': line.product_id.id or False,
            'account_analytic_id': self.project_id.analytic_account_id.id,
            'account_id': account.id,
            'price_unit': line.price_unit,
            'quantity': line.quantity,
            'name': line.description,
        }
        return line_vals


class ProjectInvoicePlanLine(models.Model):
    _name = 'project.invoice.plan.line'
    _description = 'Project invoice plan lines'

    project_invoice_plan_id = fields.Many2one(
        comodel_name='project.invoice.plan',
        string='Invoice plan',
        ondelete='cascade',
    )
    name = fields.Char(
        string='Name'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product'
    )
    currency_id = fields.Many2one(
        related='project_invoice_plan_id.currency_id',
        string='Currency',
        store=True,
        readonly=True
    )
    price_unit = fields.Float(
        string='Unit Price',
        required=True,
        digits=dp.get_precision('Product Price')
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
    )
    amount = fields.Monetary(
        string='Amount (without Taxes)',
        store=True,
        readonly=True,
        compute='_compute_amount',
    )
    description = fields.Text(
        string='Description'
    )
    account_analytic_line_ids = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='project_invoice_plan_line_id',
        string='Timesheet Lines'
    )

    @api.multi
    @api.depends('quantity', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.price_unit
