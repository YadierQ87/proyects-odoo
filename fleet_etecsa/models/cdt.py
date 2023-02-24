# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError

today = datetime.today().strftime("%d/%m/%Y")
# calculo del CDT
class fleet_etecsa_calculo_cdt(models.Model):
    _name = "fleet.etecsa.calculo.cdt"
    _description = "Coeficiente de Disponibilidad Transporte"

    name = fields.Char(default='Calculo CDT %s' % today, readonly=True)
    total_vehiculos = fields.Float(readonly=True,
                                   default=lambda self: self.env['fleet.vehicle'].search_count([]),store=True)
    vehiculos_operando = fields.Float(readonly=True,
                                      default=lambda self: self.env['fleet.vehicle'].search_count(
                                          [('state_id', '=', 'Funcionando')]),store=True)
    vehiculos_paralizados = fields.Float(readonly=True,
                                         default=lambda self: self.env['fleet.vehicle'].search_count(
                                             [('state_id', '=', 'Paralizado')]),store=True)
    vehiculos_otros = fields.Float(readonly=True)
    resultado_cdt = fields.Float('Resultado CDT %',(3, 2),readonly=True, store=True)
    entry_date = fields.Date('Fecha de Registro', default=fields.Date.today, readonly=True)


    @api.model
    def _calcular_cdt_diario(self):
        Vehicles = self.env['fleet.vehicle']
        total_vehiculos = Vehicles.search_count([])
        vehiculos_operando = Vehicles.search_count([('state_id', '=', 'Funcionando')])
        vehiculos_paralizados = Vehicles.search_count([('state_id', '=', 'Paralizado')])
        vehiculos_otros = Vehicles.search_count([('state_id', '!=', 'Paralizado')])
        if total_vehiculos == 0:
             raise UserError('Error division por zero')
        else:
             resultado_cdt = (vehiculos_otros) * 100 / total_vehiculos
             Cdt = self.env['fleet.etecsa.calculo.cdt']
             Cdt.sudo().create({
                  'total_vehiculos': total_vehiculos,
                  'vehiculos_operando': vehiculos_operando,
                  'vehiculos_paralizados': vehiculos_paralizados,
                  'resultado_cdt': resultado_cdt,
             })

