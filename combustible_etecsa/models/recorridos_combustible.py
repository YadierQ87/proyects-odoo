# -*- coding: utf-8 -*-
from odoo import models, fields, api

 # recorridos
class CombEtecsaDestinosOrigen(models.Model):
    _name = "comb.etecsa.tabla.distancia"
    _description = "Tabla de Distancia entre unidades"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Nombre del Recorrido",compute="_get_complete_name",store=True,default='New')#origen y destino
    origen = fields.Char('Origen',required=True)
    destino = fields.Char('Destino',required=True)
    vias_utilizar = fields.Char("Vías a utilizar")
    distancia_km = fields.Float("Distancia en (km)")

    def _get_complete_name(self):
        for recorrido in self:
            recorrido.name = recorrido.origen + " - " + recorrido.destino

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = vals['origen'] + " - " + vals['destino']
        result = super(CombEtecsaDestinosOrigen, self).create(vals)
        return result


class CombEtecsaRecorridosCombustible(models.Model):
    _name = "comb.etecsa.recorridos.combustible"
    _description = "Recorridos"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Recorrido")
    actividad = fields.Selection([('trabajo', 'Trabajo'), ('extra', 'Extra'), ('operacion','Operación')],default="operacion")
    recorrido = fields.Many2one('comb.etecsa.tabla.distancia',"Recorrido")
    dias_mes = fields.Integer(string= "Días/Mes")
    km_x_tabla = fields.Float(related="recorrido.distancia_km",string="Km del Recorrido")
    km_total_recorrido = fields.Float(compute='_get_compute_totales', string="Total Km")
    cantd_litros = fields.Float(compute='_get_compute_totales',string="Cantd Lts", store=True)
    demanda_comb_id = fields.Many2one("comb.etecsa.demanda.combustible")
    vehicle_id = fields.Many2one(related="demanda_comb_id.vehicle_id")
    indice_consumo = fields.Float(related="vehicle_id.indice_consumo")

    @api.one
    @api.depends('dias_mes','recorrido')
    def _get_compute_totales(self):
        if self.dias_mes and self.km_x_tabla:
            self.km_total_recorrido = self.dias_mes * self.km_x_tabla  # cálculo kms total recorridos
        if self.km_total_recorrido  > 0 and self.indice_consumo > 0:
            self.cantd_litros = self.km_total_recorrido / self.indice_consumo  # cálculo demanda


