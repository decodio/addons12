from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    timesheet_ids = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='invoice_id',
        string='Timesheet activities')
