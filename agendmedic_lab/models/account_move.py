from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    order_lab_id = fields.Many2one(
        "order.exams.lab",
        string="Orden de Laboratorio",
    )
