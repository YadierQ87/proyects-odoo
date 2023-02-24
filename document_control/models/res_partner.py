# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    document_ids = fields.One2many(
        comodel_name='document.control',
        inverse_name='partner_id',
        string='Documents',
        required=False)
    template_id = fields.Many2one(
        comodel_name='document.control.template',
        string='Template',
        required=False)
    docs_count = fields.Integer(compute="get_count_documents",string='Documents', store=True)

    @api.depends('document_ids')
    def get_count_documents(self):
        for item in self:
            if item.document_ids:
                item.docs_count = len(item.document_ids)
            else:
                item.docs_count = 0

    def return_action_view_records(self):
        """This opens the xml view with context"""
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "document_control.personal_documents_control_action_window"
        )
        action["context"] = {
            "default_partner_id": self.id,
            "default_medical_record_ids": self.document_ids,
        }
        return action

