from odoo import fields, models, api


class ResPreferences(models.Model):
    _name = 'res.preference.contact'
    _description = 'Preferencias de comunicacion de Contactos'

    name = fields.Char("Tipo de Contacto")
