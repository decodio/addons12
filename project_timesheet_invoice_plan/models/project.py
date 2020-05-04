# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    invoice_plan_ids = fields.One2many(
        comodel_name='project.invoice.plan',
        inverse_name='project_id',
        string='Invoice Plan')
    invoice_plan_item_ids = fields.One2many(
        comodel_name='project.invoice.plan.item',
        inverse_name='project_id',
        string='Invoice Plan items')
