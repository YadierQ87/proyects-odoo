from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    currency_account_ids = fields.One2many(
        "res.partner.currency.account",
        "partner_id",
        string="Currency Accounts",
        help="Configure accounts payable and receivable per currency.",
    )


class ResPartnerCurrencyAccount(models.Model):
    _name = "res.partner.currency.account"
    _description = "Currency-Specific Accounts for Partners"

    partner_id = fields.Many2one(
        "res.partner", string="Partner", required=True, ondelete="cascade"
    )
    currency_id = fields.Many2one("res.currency", string="Currency", required=True)
    receivable_account_id = fields.Many2one(
        "account.account",
        string="Receivable Account",
        domain="[('account_type', '=', 'asset_receivable')]",
    )
    payable_account_id = fields.Many2one(
        "account.account",
        string="Payable Account",
        domain="[('account_type', '=', 'liability_payable')]",
    )
