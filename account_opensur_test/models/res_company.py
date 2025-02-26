from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    rounding_difference_amount = fields.Float(
        string="Rounding Difference Amount",
        help="Maximum allowed rounding difference for balance control in Base Currency.",
        compute="_compute_values_setting",
        inverse="_set_values_setting",
    )

    rounding_difference_usd = fields.Float(
        string="Rounding Difference Amount (USD)",
        help="Maximum allowed rounding difference for balance control in USD.",
        compute="_compute_values_setting",
        inverse="_set_values_setting",
    )

    rounding_gain_account_id = fields.Many2one(
        "account.account",
        string="Rounding Gain Account",
        help="Account to register rounding gains.",
        compute="_compute_values_setting",
        inverse="_set_values_setting",
    )

    rounding_loss_account_id = fields.Many2one(
        "account.account",
        string="Rounding Loss Account",
        help="Account to register rounding losses.",
        compute="_compute_values_setting",
        inverse="_set_values_setting",
    )

    def _compute_values_setting(self):
        """Retrieve the settings from ir.config_parameter and convert to correct types"""
        parameter = self.env["ir.config_parameter"].sudo()
        for company in self:
            company.rounding_difference_amount = float(
                parameter.get_param(
                    "account_opensur_test.rounding_difference_amount", default=0.04
                )
            )
            company.rounding_difference_usd = float(
                parameter.get_param(
                    "account_opensur_test.rounding_difference_usd", default=0.01
                )
            )

            rounding_gain_account_id = parameter.get_param(
                "account_opensur_test.rounding_gain_account_id"
            )
            rounding_loss_account_id = parameter.get_param(
                "account_opensur_test.rounding_loss_account_id"
            )

            company.rounding_gain_account_id = (
                int(rounding_gain_account_id) if rounding_gain_account_id else False
            )
            company.rounding_loss_account_id = (
                int(rounding_loss_account_id) if rounding_loss_account_id else False
            )

    def _set_values_setting(self):
        """Update the settings in ir.config_parameter when modified in res.company"""
        parameter = self.env["ir.config_parameter"].sudo()
        for company in self:
            parameter.set_param(
                "account_opensur_test.rounding_difference_amount",
                str(company.rounding_difference_amount),
            )
            parameter.set_param(
                "account_opensur_test.rounding_difference_usd",
                str(company.rounding_difference_usd),
            )
            parameter.set_param(
                "account_opensur_test.rounding_gain_account_id",
                (
                    str(company.rounding_gain_account_id.id)
                    if company.rounding_gain_account_id
                    else ""
                ),
            )
            parameter.set_param(
                "account_opensur_test.rounding_loss_account_id",
                (
                    str(company.rounding_loss_account_id.id)
                    if company.rounding_loss_account_id
                    else ""
                ),
            )
