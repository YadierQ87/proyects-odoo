# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
MONTHS = [
            ('1', 'Enero'),
            ('2', 'Febrero'),
            ('3', 'Marzo'),
            ('4', 'Abril'),
            ('5', 'Mayo'),
            ('6', 'Junio'),
            ('7', 'Julio'),
            ('8', 'Agosto'),
            ('9', 'Septiembre'),
            ('10', 'Octubre'),
            ('11', 'Noviembre'),
            ('12', 'Diciembre'),
        ]

months_all = [
            'Enero',
            'Febrero',
            'Marzo',
            'Abril',
            'Mayo',
            'Junio',
            'Julio',
            'Agosto',
            'Septiembre',
            'Octubre',
            'Noviembre',
            'Diciembre'
        ]


class AccountMove(models.Model):
    _inherit = "account.move"

    property_id = fields.Many2one(
        "property.building",
        related="partner_id.property_id",
        string="Department")
    year = fields.Char(readonly=True, string="Year")
    month = fields.Selection(
        string='Month of invoice',
        selection=MONTHS,
        required=False,
        readonly=True,
    )
    month_before = fields.Char(
        string='Mes anterior',
        compute='get_month_before',
        required=False)
    is_alipayment = fields.Boolean(readonly=True)

    month_report = fields.Selection(
        string='S_Mes',
        selection=MONTHS,
        required=False
    )

    @api.depends('month')
    def get_month_before(self):
        if self.month:
            self.month_before = months_all[int(self.month)-1]

    _sql_constraints = [
        ('alipayment_uniq',
         'unique (is_alipayment,partner_id,month,year,move_type)',
         'Only one Alipayment for month and property is allowed!')]

    def action_send_invoice_whatsapp(self):
        """Enviar el consumo de alicuota en un mensaje whatsapp"""
        contact = self.partner_id.id
        presentation = " Hola %s " % self.partner_id.name
        month_id = months_all[int(self.month)-1]
        message = "Se envia el reporte de consumo de Alicuota para el mes de %s" % month_id
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        link_invoice = "%s/report/pdf/ot_alipayments.invoice_report_consumption/%s" % (base_url, self.id)
        table = " NOTIFICACION DE ALICUOTA  \n FECHA: %s \n DEPARTAMENTO %s \n" \
                " CONSUMO CORRESPONDIENTE AL MES DE: %s \n" \
                "RUBRO | LECTURA ANTERIOR | LECTURA ACTUAL | CONSUMO " \
                "| VALOR" % (self.invoice_date, self.property_id.name, month_id)
        quotes_lines = ""
        for line in self.invoice_line_ids:
            quotes_lines += "%s - %s - %s - %s - %s \n" % \
                            (line.name, line.previous_consumption, line.actual_consumption, line.consumption,
                             line.price_subtotal)
        greeting = "Ud. puede consultar el documento original aqui \n %s" % link_invoice
        return {
            "type": "ir.actions.act_window",
            "name": _("Whatsapp Message"),
            "res_model": "whatsapp.lab.message.wizard",
            "target": "new",
            "view_mode": "form",
            "view_type": "form",
            "context": {
                "default_user_id": contact,
                "default_mobile": self.partner_id.mobile,
                "default_message": "%s \n %s \n %s " % (presentation, message, greeting),
            },
        }
