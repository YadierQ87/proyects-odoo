# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DocumentCategory(models.Model):
    _name = 'document.control.category'
    _description = 'Category for document control'

    name = fields.Char()


class DocumentControl(models.Model):
    _name = 'document.control'
    _description = 'Document Control'

    name = fields.Char()
    reference = fields.Char(
        string='Reference',
        default='New',
        readonly=True,
        required=False)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact')
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env['res.users'].browse(self.env.uid).company_id.id,
        string='Company')
    category_id = fields.Many2one(
        comodel_name='document.control.category',
        string='Category',
        required=True)
    expiration_date = fields.Date(
        string='Expiration date',
        default=fields.Date.today(),
        required=False)
    status = fields.Selection(
        string='Status',
        selection=[
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('expired', 'Expired'),
            ('cancel', 'Cancel'),
        ],
        default='draft',
        tracking=True)
    file = fields.Binary(string="File",required=False  )
    expiration_type = fields.Selection(
        string='Expiration type',
        selection=[('date', 'date'),
                   ('other', 'other'), ],
        required=False, )
    description = fields.Text(
        string="Description",
        required=False)

    @api.model
    def create(self, vals):
        if vals.get('reference', 'New') == 'New':
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'document.control') or 'New'
        result = super(DocumentControl, self).create(vals)
        return result


class LineControlTemplate(models.Model):
    _name = 'line.control.template'
    _description = 'Lines for document control in template'

    name = fields.Char()
    block_sale = fields.Boolean(
        string='Block for sale',
        required=False)
    template_id = fields.Many2one(
        comodel_name='document.control.template',
        string='Template',
        required=False)



class DocumentTemplate(models.Model):
    _name = 'document.control.template'
    _description = 'Template for document control'

    name = fields.Char()
    category_id = fields.Many2one(
        comodel_name='document.control.category',
        string='Category',
        required=True)
    control_line_ids = fields.One2many(
        comodel_name='line.control.template',
        inverse_name='template_id',
        string='Documents',
        required=False)



