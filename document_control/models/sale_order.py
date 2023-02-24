# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('partner_id')
    def _check_template_documents(self):
        if self.partner_id.template_id:
            if self.partner_id.document_ids:
                docs_template = self.partner_id.template_id.control_line_ids
                docs_partner = self.partner_id.document_ids
                control_blocks = 0
                control_files = 0
                for doc in docs_template:
                    if doc.block_sale:
                        control_blocks+= 1
                        for file in docs_partner:
                            if doc.name == file.name:
                                control_files += 1
                                if file.status != 'confirm':
                                    raise ValidationError('The client has a required document [%s] expired or cancel' % file.name)
                if control_files != control_blocks:
                    raise ValidationError('The client has a missing required document!')

