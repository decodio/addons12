# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectInvoicePlan(models.Model):
    _name = 'project.invoice.plan'
    _description = 'Invoice plan from Project'
    _order = 'invoice_date desc'

    name = fields.Char(
        string='Name')
    invoice_date = fields.Date(
        string='Invoice Date')
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice')
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project')
    invoice_plan_item_ids = fields.One2many(
        comodel_name='project.invoice.plan.item',
        inverse_name='plan_id',
        string='Items/Lines'
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency', )
    description = fields.Text('Description')
    note = fields.Text('Note')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company', )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('invoiced', 'invoiced'),
            ('cancel', 'Canceled')
        ], string='State', default='draft'
    )


class ProjectInvoicePlanItem(models.Model):
    _name = 'project.invoice.plan.item'
    _description = 'Project invoice plan items'

    name = fields.Char(
        string='Name')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
    )
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
    )
    plan_id = fields.Many2one(
        comodel_name='project.invoice.plan',
        string='Invoice plan',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product'
    )
    price_unit = fields.Float(
        string='Price Price',
        # required=False,
        # digits=dp.get_precision('Account'),
    )
    quantity = fields.Float(
        string='Quantity',
        # digits=dp.get_precision('Account'),
        # digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True,
    )
    amount = fields.Float(
        string='Line value',
        # required=False,
        # compute=False,
        # digits=dp.get_precision('Account'),
        help="Line value  without tax = Price * Quantity"
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
    )


    description = fields.Text('Description')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner')
