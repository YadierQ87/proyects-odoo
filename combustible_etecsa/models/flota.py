# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

#parametros ponderacion para la asignacion de combustible
class ParametrosPonderados(models.Model):
    _name = "comb.parametros.ponderados.vehicle"

    name = fields.Char(string="Nombre del Parametro")
    valor = fields.Integer(string="Valor del Parametro")

#clase que hereda de vehiculo y lo modifica
class fleet_etecsa_vehicle(models.Model):
    _name = "fleet.vehicle"
    _inherit = ["fleet.vehicle"] #heredando y sobreescribiendo metodos o atributos

    indice_consumo = fields.Float(string = "Índice de Consumo")
    prioridad = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')],
                                 string="Prioridad en base calculo de combustible",
                                 help="Prioridad para el calculo del combustible",
                                 default="1")
    ponderacion = fields.Float(compute="_compute_total_parametros",string = "Nivel de prioridad",default=1)
    parent_id_department = fields.Many2one(related='depto_propietario.parent_id')
    parametros_ids = fields.Many2many("comb.parametros.ponderados.vehicle")
    tarjeta = fields.Char("Tarjeta de Combustible")
    fuel_type = fields.Selection(
        [("Diesel", "Diesel"), ("Gasolina Especial", "Gasolina Especial"), ("Gasolina Regular", "Gasolina Regular"),
         ("Eléctrico", "Eléctrico"), ("Híbrido", "Híbrido")])
    #tarjeta = fields.Many2one("fleet.etecsa.tarjeta.combustible")

    @api.depends('parametros_ids')
    def _compute_total_parametros(self):
        self.ponderacion = 1 #minimo de ponderacion es 1
        total_pond = 0
        if self.parametros_ids:
            for param in self.parametros_ids:
                total_pond += param.valor
        if total_pond > 0 and total_pond <= 10:
            self.ponderacion = total_pond
        if total_pond > 0 and total_pond > 10:
            self.ponderacion = 10 #maximo de ponderacion es 10







