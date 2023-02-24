# -*- coding: utf-8 -*-
from odoo import models, fields, api,tools, _

#Locales
class SerclinicLocalsMedicalEquipment(models.Model):
    _name = 'serclinic.local.medical.equipment'
    _description = 'Local de Equipos'
    name = fields.Char(string='Nombre')
    state = fields.Selection([("Apto","Apto"),("No Apto","No Apto")],default="Apto")
    active = fields.Boolean('Activo?', default=True)
    observation = fields.Text('Observaciones')
    local_address = fields.Char('Direccion del Local')


#Tipo de Equipos Medicos
class SerclinicCodEquipmentType(models.Model):
    _name = 'serclinic.cod.equipment.type'
    _description = 'Tipo de Equipos'
    name = fields.Char(string='Nombre Tipo Equipo')
    state = fields.Selection([("Apto","Apto"),("No Apto","No Apto")],default="Apto")
    observation = fields.Text('Observaciones')






