# -*- coding: utf-8 -*-

from odoo import models, api, fields


class WhatsappLabMessage(models.TransientModel):
    _name = 'whatsapp.lab.message.wizard'
    _description = "Whatsapp Wizard for Labs"

    user_id = fields.Many2one('res.partner', string="Enviar a:", required=True)
    mobile = fields.Char(required=True, string="Teléfono")
    message = fields.Text(string="Mensaje", required=True)

    def send_whatsapp_message(self):
        if self.message and self.mobile:
            message_string = ''
            message = self.message.split(' ')
            for msg in message:
                message_string = message_string + msg + '%20'
            message_string = message_string[:(len(message_string) - 3)]
            return {
                'type': 'ir.actions.act_url',
                'url': "https://api.whatsapp.com/send?phone="+self.mobile+"&text=" + message_string,
                'target': 'new',
                'res_id': self.id,
            }
