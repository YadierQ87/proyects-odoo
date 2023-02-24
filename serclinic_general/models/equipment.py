# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import date,datetime
from dateutil.relativedelta import relativedelta

#Equipos Medicos
class SerclinicMedicalEquipment(models.Model):
    _name = 'serclinic.medical.equipment'
    _description = 'Medical Equipment'

    name = fields.Char(string='Nombre del Equipo')
    inventary = fields.Char(string='No Inventario')
    local_id = fields.Many2one('serclinic.local.medical.equipment',string="Local del Equipo",required=True)
    equipment_type_id = fields.Many2one('serclinic.cod.equipment.type',string="Tipo de Equipo",required=True)
    active = fields.Boolean('Activo?', default=True)
    state = fields.Selection([("Apto","Apto"),("No Apto","No Apto")])
    last_calibration_date = fields.Date("Ultima fecha de calibración",default=fields.Date.today)
    last_certification_date = fields.Date("Ultimo certificado de calibración",default=fields.Date.today)
    production_date = fields.Date("Fecha de producción",required=True,default=fields.Date.today)
    model = fields.Char('Modelo del equipo')
    mark = fields.Char('Marca del equipo')
    qty_users = fields.Integer('Cantidad de Usuarios')
    observation = fields.Text('Observaciones')


