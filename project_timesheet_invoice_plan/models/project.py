# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    invoice_plan_ids = fields.One2many(
        comodel_name='project.invoice.plan',
        inverse_name='project_id',
        string='Invoice Plan')

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        readonly=False,
        required=True,
        default=lambda self: self._get_default_currency_id(),
        track_visibility='onchange',
    )

    def _get_default_currency_id(self):
        return self.company_id.currency_id \
            or self.env.user.company_id.currency_id
