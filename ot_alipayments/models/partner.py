# -*- coding: utf-8 -*-
from datetime import datetime, date

from odoo import api, fields, models, _

import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PropertyBuilding(models.Model):
    _name = 'property.building'
    _description = 'Property building'

    name = fields.Char()
    description = fields.Text()
    company_id = fields.Many2one("res.company", string="Condominium")
    ali_payment = fields.Float(string="Alipayment")


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_client = fields.Boolean("Is tenant")
    property_id = fields.Many2one(
        "property.building",
        string="Department")
    ali_payment = fields.Float(
        related="property_id.ali_payment",
        string="Alipayment")
    condominium_id = fields.Many2one(
        "res.company",
        related="property_id.company_id",
        store=True,
        string="Condominium")
    services_ids = fields.Many2many(
        comodel_name='product.product',
        string='Condominium Services')
    last_month_invoiced = fields.Selection(
        string='Last Month Invoiced',
        selection=[
            ('1', 'January'),
            ('2', 'February'),
            ('3', 'March'),
            ('4', 'April'),
            ('5', 'May'),
            ('6', 'June'),
            ('7', 'July'),
            ('8', 'August'),
            ('9', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'December'),
        ],
        required=False, )

    def get_current_company(self):
        return self.env.user.company_id.id

    def get_debit_account_account(self, company_id):
        """Account for debit"""
        # Code: 1102050101
        # Account Name: Cuentas por cobrar clientes
        AccountAccount = self.env['account.account']
        if not company_id:
            company_id = self.get_current_company()
        account = AccountAccount.search(
            [('code', '=', '1102050101'), ('company_id', '=', company_id)], limit=1)
        if account:
            return account.id
        return False

    def get_credit_account_account(self, company_id):
        """Account for credit"""
        # Code:  410201 Account Name:   Prestacion de Servicios
        AccountAccount = self.env['account.account']
        if not company_id:
            company_id = self.get_current_company()
        account = AccountAccount.search(
            [('code', '=', '410201'), ('company_id', '=', company_id)], limit=1)
        if account:
            return account.id
        return False

    def get_journal_id(self, company_id):
        """return special journal created for ALICUOTAS only"""
        journal_id = self.env['account.journal'].search(
            [
                ('type', '=', 'sale'),
                ('code', '=', 'ALI'),
                ('company_id', '=', company_id),
            ], limit=1)
        if journal_id:
            return journal_id.id
        else:
            raise ValidationError('El diario de Cobro de Alícuotas no se ha creado en la compañia %s!' % company_id)

    def create_invoice_month(self, partner, company, month, year, building):
        Invoice = self.env['account.move']
        Product = self.env['product.product']
        ali_payment = Product.search([('name', '=', 'Alicuota')])
        invoice_data = {
            "partner_id": partner.id,
            "invoice_date": date.today(),
            "payment_reference": "AliCuota-Condominio",
            "property_id": building.id,
            "move_type": "out_invoice",
            "journal_id": self.get_journal_id(company.id),
            "company_id": company.id,
            "month": str(month),
            "year": str(year),
            "is_alipayment": True,
            "amount_total": building.ali_payment,
        }
        new_invoice = Invoice.create(invoice_data)
        # create the first line for Alicuota
        new_invoice.write({
            "invoice_line_ids": [(0, 0, {
                "product_id": ali_payment.id,
                "name": ali_payment.name,
                "move_id": new_invoice.id,
                "account_id": self.get_credit_account_account(company.id),  #
                "quantity": 1,
                "price_unit": building.ali_payment,
            })]
        })
        previous_invoice = self._get_previous_invoice(partner.id, month, year)
        for service in partner.services_ids:
            new_invoice.write({
                "invoice_line_ids": [(0, 0, {
                    "product_id": service.id,
                    "name": service.name,
                    "previous_consumption": self.get_previous_consumption(previous_invoice, service.id),
                    "move_id": new_invoice.id,
                    "account_id": self.get_credit_account_account(company.id),
                    "quantity": 1,
                    "price_unit": service.lst_price,
                })]
            })
        partner.write({'last_month_invoiced': str(month)})

    def _get_previous_invoice(self, partner_id, month, year):
        month_before = 12 if month == 1 else month - 1
        year = year - 1 if month_before == 12 else year
        previous_invoice = self.env['account.move'].search(
            [
                ('month', '=', str(month_before)),
                ('partner_id', '=', partner_id),
                ('is_alipayment', '=', True),
                ('year', '=', str(year)),
            ])
        if previous_invoice:
            return previous_invoice
        return False

    @staticmethod
    def get_previous_consumption(previous_invoice, product_id):
        previous_consumption = 0.00
        if previous_invoice:
            for line in previous_invoice.invoice_line_ids:
                if line.product_id.id == product_id:
                    previous_consumption = line.previous_consumption
        return previous_consumption

    def cron_account_move_current_month(self):
        current_month = datetime.now().month
        current_year = datetime.now().year
        current_day = datetime.now().day
        all_tenants = self.env['res.partner'].search([('is_client', '=', 'True')])
        for tenant in all_tenants:
            company_id = tenant.property_id.company_id
            if current_day >= 24:  # run the method for the next-month
                next_month = current_month + 1
                if current_month == 12 and int(tenant.last_month_invoiced) == 12:
                    next_month = 1
                    self.create_invoice_month(tenant, company_id, next_month, current_year, tenant.property_id)
                if (int(tenant.last_month_invoiced) + 1) == next_month:
                    self.create_invoice_month(tenant, company_id, next_month, current_year, tenant.property_id)
            else:
                if current_month == 1 and int(tenant.last_month_invoiced) == 12:
                    self.create_invoice_month(tenant, company_id, current_month, current_year, tenant.property_id)
                if 1 < current_month <= 12:
                    if (int(tenant.last_month_invoiced) + 1) == current_month:
                        self.create_invoice_month(tenant, company_id, current_month, current_year, tenant.property_id)

    def _get_amounts_and_date(self):
        #company = self.env.user.company_id
        company_ids = self.env.user.company_ids
        current_date = fields.Date.today()
        for partner in self:
            worst_due_date = False
            amount_due = amount_overdue = 0.0
            for aml in partner.unreconciled_aml_ids:
                if (aml.company_id in company_ids):
                    date_maturity = aml.date_maturity or aml.date
                    if not worst_due_date or date_maturity < worst_due_date:
                        worst_due_date = date_maturity
                    amount_due += aml.result
                    if (date_maturity <= current_date):
                        amount_overdue += aml.result
            partner.payment_amount_due = amount_due
            partner.payment_amount_overdue = amount_overdue
            partner.payment_earliest_due_date = worst_due_date
