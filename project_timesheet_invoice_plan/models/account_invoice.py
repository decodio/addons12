# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    project_id = fields.Many2one(
        comodel_name='project.project',
        string="Project"
    )
