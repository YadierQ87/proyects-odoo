from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    rounding_difference_amount = fields.Float(
        default=0.04, string="Rounding Difference Amount"
    )
    rounding_difference_usd = fields.Float(
        default=0.01, string="Rounding Difference Amount (USD)"
    )
    rounding_gain_account_id = fields.Many2one("account.account")
    rounding_loss_account_id = fields.Many2one("account.account")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].set_param(
            "account_opensur_test.rounding_difference_amount",
            self.rounding_difference_amount,
        )
        self.env["ir.config_parameter"].set_param(
            "account_opensur_test.rounding_difference_usd", self.rounding_difference_usd
        )
        self.env["ir.config_parameter"].set_param(
            "account_opensur_test.rounding_gain_account_id",
            self.rounding_gain_account_id.id,
        )
        self.env["ir.config_parameter"].set_param(
            "account_opensur_test.rounding_loss_account_id",
            self.rounding_loss_account_id.id,
        )

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icp = self.env["ir.config_parameter"]  # Alias para simplificar llamadas

        rounding_difference_amount = icp.get_param(
            "account_opensur_test.rounding_difference_amount", default=0.04
        )
        rounding_difference_usd = icp.get_param(
            "account_opensur_test.rounding_difference_usd", default=0.01
        )

        # Recuperar valores como string y convertir a entero si existen
        rounding_gain_account_id = icp.get_param(
            "account_opensur_test.rounding_gain_account_id"
        )
        rounding_loss_account_id = icp.get_param(
            "account_opensur_test.rounding_loss_account_id"
        )

        res.update(
            {
                "rounding_difference_amount": float(rounding_difference_amount),
                "rounding_difference_usd": float(rounding_difference_usd),
                "rounding_gain_account_id": (
                    int(rounding_gain_account_id) if rounding_gain_account_id else False
                ),
                "rounding_loss_account_id": (
                    int(rounding_loss_account_id) if rounding_loss_account_id else False
                ),
            }
        )
        return res
