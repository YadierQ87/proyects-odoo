# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # invoice_line_ids
    previous_consumption = fields.Float(
        string='Lectura Anterior',
        store=True,
        required=False)
    actual_consumption = fields.Float(
        string='Lectura Actual',
        store=True,
        required=False)
    consumption = fields.Float(string='Consumo',
                               store=True,
                               compute='_onchange_consumption',
                               default=0.0)

    @api.depends('actual_consumption', 'previous_consumption')
    def _onchange_consumption(self):
        for item in self:
            if item.previous_consumption < item.actual_consumption:
                item.consumption = item.actual_consumption - item.previous_consumption
            if item.consumption != 0:
                item.quantity = item.consumption
