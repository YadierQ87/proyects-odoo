from odoo import fields, models, api


class FeeType(models.Model):
    _name = 'house.fee.type'
    _description = 'Fee Type'

    name = fields.Char()


class Contracts(models.Model):
    _name = 'house.contract.client'
    _description = 'Contracts for clients'

    name = fields.Char()
    property_id = fields.Many2one(
        comodel_name='house.property',
        string='House Property',
        required=True)
    customer_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        required=True)
    scan_document = fields.Binary(string="Scanned Document",)
    fee_type = fields.Many2one(
        comodel_name='house.fee.type',
        string='Fee Type',
        required=True)
    date_start = fields.Datetime(string='Start of contract')
    date_end = fields.Datetime(string='End of Contract')
    state = fields.Selection(
        string='State',
        selection=[
            ('active', 'active'),
            ('inactive', 'inactive'),
            ('closed', 'closed'),
        ],
        required=False, )
    total_amount = fields.Float(
        string='Total Amount',
        required=False)
    total_paid = fields.Float(
        string='Total Paid',
        required=False)
    payment_lines_ids = fields.One2many(
        comodel_name='house.contract.payment.lines',
        inverse_name='contract_id',
        string='Payment lines',
        required=False)


class PaymentLines(models.Model):
    _name = 'house.contract.payment.lines'
    _description = 'Payment Lines for contracts'

    name = fields.Char()  # TODO set the sequence for [house.contract.payment.lines]
    contract_id = fields.Many2one(
        comodel_name='house.contract.client',
        string='Contract',
        required=True)
    description = fields.Char()
    fee_type = fields.Many2one(
        comodel_name='house.fee.type',
        string='Fee type',
        required=False)
    payment_date = fields.Date(
        string='Payment date',
        required=False)
    amount = fields.Float()
    status = fields.Selection([
        ('paid', 'paid'), ('not paid', 'not paid')])







