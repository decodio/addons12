
from odoo import models, fields


class IrTranslation(models.Model):
    _inherit = 'ir.translation'

    type = fields.Selection(selection_add=[('report', 'Report')],)