from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    only_base_currency = fields.Boolean(
        string="Only Base Currency",
        help="Indicates if the journal entry will only be handled in the company's base currency.",
    )

    # paso 4
    @api.constrains("line_ids")
    def _check_balance_usd(self):
        for move in self:
            total_debit_usd = sum(move.line_ids.mapped("debit_usd"))
            total_credit_usd = sum(move.line_ids.mapped("credit_usd"))

            if total_debit_usd != total_credit_usd:
                raise ValidationError(
                    "The journal entry is not balanced in USD. Total Debit USD must match Total Credit USD."
                )

    # paso 5 inciso d)
    def _check_rounding_difference(self):
        """Check if the journal entry has a rounding difference and handle it."""
        for move in self:
            company = move.company_id
            rounding_setting_base = company.rounding_difference_amount  # 0.04
            rounding_setting_usd = company.rounding_difference_usd  # 0.01

            # Calcular totales en moneda base y USD
            total_debit = sum(
                move.line_ids.mapped("debit")
            )  # suma de todos los debitos 158.36
            total_credit = sum(
                move.line_ids.mapped("credit")
            )  # suma de todos los creditos 158.35
            total_debit_usd = sum(move.line_ids.mapped("debit_usd"))  # 3.65
            total_credit_usd = sum(move.line_ids.mapped("credit_usd"))  # 3.65

            # Determinar si hay diferencia en moneda  o en USD
            rounding_diff_base = round(total_debit - total_credit, 2)
            rounding_diff_usd = round(total_debit_usd - total_credit_usd, 2)

            # Comprobar si el asiento tiene al menos un apunte en otra moneda
            has_foreign_currency = any(
                line.currency_id and line.currency_id != company.currency_id
                for line in move.line_ids
            )

            new_move_lines = []

            #  Importe Diferencia por redondeo
            if (
                has_foreign_currency
                and abs(rounding_diff_base) <= rounding_setting_base
            ):
                if (
                    not company.rounding_gain_account_id
                    or not company.rounding_loss_account_id
                ):
                    raise UserError(
                        _(
                            "Rounding difference detected, but the company has not configured rounding gain/loss accounts."
                        )
                    )

                new_move_lines.append(
                    {
                        "account_id": (
                            company.rounding_gain_account_id.id
                            if rounding_diff_base < 0
                            else company.rounding_loss_account_id.id
                        ),
                        "debit": (
                            abs(rounding_diff_base) if rounding_diff_base > 0 else 0.0
                        ),
                        "credit": (
                            abs(rounding_diff_base) if rounding_diff_base < 0 else 0.0
                        ),
                        "move_id": move.id,
                    }
                )

            # Manejo de redondeo en USD
            if abs(rounding_diff_usd) <= rounding_setting_usd:
                if (
                    not company.rounding_gain_account_id
                    or not company.rounding_loss_account_id
                ):
                    raise UserError(
                        _(
                            "Rounding difference detected in USD, but the company has not configured rounding gain/loss accounts."
                        )
                    )

                new_move_lines.append(
                    {
                        "account_id": (
                            company.rounding_gain_account_id.id
                            if rounding_diff_usd < 0
                            else company.rounding_loss_account_id.id
                        ),
                        "debit_usd": (
                            abs(rounding_diff_usd) if rounding_diff_usd > 0 else 0.0
                        ),
                        "credit_usd": (
                            abs(rounding_diff_usd) if rounding_diff_usd < 0 else 0.0
                        ),
                        "move_id": move.id,
                    }
                )

            # Crear apuntes de corrección si es necesario
            if new_move_lines:
                self.env["account.move.line"].create(new_move_lines)

    def _post(self, soft=True):
        """
        Override _post() method to ensure the rounding difference is checked before posting the journal entry.
        """
        # Verificar la diferencia de redondeo antes de contabilizar
        self._check_rounding_difference()
        # # verificar si es factura de cliente o proveedor y cargar la cuenta de la moneda del partner
        if self.is_invoice():
            account = self._get_partner_currency_account()
            if account:
                for line in self.line_ids.filtered(
                    lambda l: l.account_id.account_type
                    in ["asset_receivable", "liability_payable"]
                ):
                    line.account_id = account

        return super(AccountMove, self)._post(soft=soft)

    # paso 6
    def _get_partner_currency_account(self):
        """Obtener la cuenta correcta de acuerdo con la moneda de la factura y el partner."""
        for move in self:
            if move.partner_id and move.currency_id:
                # Buscar si el partner tiene una cuenta configurada para esta moneda
                currency_account = move.partner_id.currency_account_ids.filtered(
                    lambda c: c.currency_id == move.currency_id
                )

                # Determinar si es factura de cliente o proveedor
                if move.move_type in [
                    "out_invoice",
                    "out_refund",
                ]:  # Factura de venta o Nota de crédito
                    return (
                        currency_account[:1].receivable_account_id
                        if currency_account
                        else move.partner_id.property_account_receivable_id
                    )
                elif move.move_type in [
                    "in_invoice",
                    "in_refund",
                ]:  # Factura de compra o Nota de débito
                    return (
                        currency_account[:1].payable_account_id
                        if currency_account
                        else move.partner_id.property_account_payable_id
                    )
        return None


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    debit_usd = fields.Monetary(
        string="Debit USD",
        currency_field="company_currency_id",
        store=True,
        readonly=True,
        compute="_compute_usd_amounts",
    )
    credit_usd = fields.Monetary(
        string="Credit USD",
        currency_field="company_currency_id",
        store=True,
        readonly=True,
        compute="_compute_usd_amounts",
    )
    balance_usd = fields.Monetary(
        string="Balance USD",
        currency_field="company_currency_id",
        store=True,
        readonly=True,
        compute="_compute_balance_usd",
    )

    @api.depends(
        "amount_currency",
        "currency_id",
        "move_id.only_base_currency",
        "move_id.date",
        "credit",
        "debit",
    )
    def _compute_usd_amounts(self):
        to_currency = self.env["res.currency"].search([("name", "=", "USD")], limit=1)
        for line in self:
            if line.move_id.only_base_currency:
                line.debit_usd = 0.0
                line.credit_usd = 0.0
                continue

            if line.currency_id and line.currency_id.name == "USD":
                amount = line.amount_currency
            else:
                # buscar el USD para convertir
                amount = line.currency_id._convert(
                    line.amount_currency,
                    to_currency,
                    self.env.company,
                    line.move_id.date,
                )

            line.debit_usd = amount if amount > 0 else 0.0
            line.credit_usd = -amount if amount < 0 else 0.0

    @api.depends("debit_usd", "credit_usd")
    def _compute_balance_usd(self):
        for line in self:
            line.balance_usd = line.debit_usd - line.credit_usd

    @api.constrains("debit_usd", "credit_usd")
    def _check_debit_credit_usd(self):
        for line in self:
            if line.debit_usd and line.credit_usd:
                raise models.ValidationError(
                    "An accounting entry cannot have values in both Debit USD and Credit USD at the same time."
                )
