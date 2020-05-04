# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    invoice_plan_item_id = fields.Many2one(
        comodel_name='project.invoice.plan.item',
        string='Invoice plan item',
    )
    invoice_id = fields.Many2one(
        comodel_name='account.invoice'
    )
