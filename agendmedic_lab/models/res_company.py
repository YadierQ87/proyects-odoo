# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.company"

    header_report_bg = fields.Binary(
        string="Header Background para el reporte medico",
    )
    lateral_report_bg = fields.Binary(
        string="Lateral Background para el reporte medico",
    )
    footer_report_bg = fields.Binary(
        string="Footer Background para el reporte medico",
    )

    def get_header_attachment(self):
        attachment_id = self.env["ir.attachment"].search(
            [
                ("name", "=", "laboratory_report_header.png"),
                ("res_model", "=", "ir.ui.view"),
            ]
        )
        return attachment_id

    def get_lateral_attachment(self):
        attachment_id = self.env["ir.attachment"].search(
            [
                ("name", "=", "report_lateral.jpg"),
                ("res_model", "=", "ir.ui.view"),
            ]
        )
        return attachment_id

    def get_footer_attachment(self):
        attachment_id = self.env["ir.attachment"].search(
            [
                ("name", "=", "laboratory_report_footer.png"),
                ("res_model", "=", "ir.ui.view"),
            ]
        )
        return attachment_id


