# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError

 #costo del combustible
class CombCostoLitro(models.Model):
    _name = "comb.costo.litro"
    _description = "Costo del Litro"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char( readonly=True,compute="_get_name_costo")
    tipo_combustible = fields.Selection(
        [("Diesel", "Diesel"), ("Gasolina Especial", "Gasolina Especial"), ("Gasolina Regular", "Gasolina Regular")],required=True)
    costo = fields.Float(required=True)

    def _get_name_costo(self):
        for costo in self:
            costo.name = "Precio de " + costo.tipo_combustible

    _sql_constraints = [
        ('demanda_costo_litro_uniq',
         'UNIQUE (tipo_combustible, name)',
         'Solo puede existir un precio  por tipo de combustible!')]


class CombEtecsaDemandaDepartamento(models.Model):
    _name = "comb.etecsa.demanda.departamento"
    _description = "Demanda Departamento"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Demanda del Departamento", readonly=True,
                       required=True, copy=False, default='New', order="desc")
    estado = fields.Selection([('demandado', 'Demandado'),
                               ('asignado', 'Asignado'),
                               ('aprobado', 'Aprobado'),
                               ('rechazado', 'Rechazado')],
                              string="Estado Demanda por Dpto.",default="demandado")
    departamento_id = fields.Many2one("hr.department")
    costo_litro = fields.Float(compute="_get_costo_litro")
    tipo_combustible = fields.Selection([("Diesel", "Diesel"), ("Gasolina Especial", "Gasolina Especial"), ("Gasolina Regular", "Gasolina Regular")])
    fecha_ini = fields.Date("Fecha Inicio")
    fecha_fin = fields.Date("Fecha Fin")
    active = fields.Boolean("Active?", default=True,
                            track_visibility="always")
    mes_demanda = fields.Selection([('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
                                    ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
                                    ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
                                    ('12', 'Diciembre')])
    nombre_jefe = fields.Many2one(related="departamento_id.manager_id",store=True, string="Responsable")
    observaciones = fields.Char("Observaciones")
    demanda_combt_ids = fields.One2many("comb.etecsa.demanda.combustible","demanda_dpto_id",string="Demanda Dpto")
    verificar_estado = fields.Char(store=True)
    tipo_demanda = fields.Selection(
        [('normal', 'normal'),
         ('segunda-vuelta', 'segunda-vuelta'),
         ('demanda-extra', 'demanda-extra'),
         ('emergencia', 'emergencia'), ],
        string="Estado de la Demanda", default="normal")

    @api.depends('tipo_combustible')
    def _get_costo_litro(self):
        if self.tipo_combustible:
            self.costo_litro = self.env["comb.costo.litro"].search([('tipo_combustible','=',self.tipo_combustible)]).costo
        else:
            self.costo_litro = 0.00

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code('comb.etecsa.demanda.combustible.depto') or 'New'
            if self.departamento_id.name:
                vals['name'] = seq + (self.departamento_id.name)
            else:
                vals['name'] = seq
        result = super(CombEtecsaDemandaDepartamento, self).create(vals)
        return result

    #se generan todas las demandas de vehiculos de ese depto para ese mes y tipo de combustible
    def do_listar_demandas_depto(self):
        if self.tipo_combustible and self.mes_demanda and self.departamento_id:
            #Crear todas las demandas del depto segun los vehiculos registrados para su nivel
            CombDemanda = self.env["comb.etecsa.demanda.combustible"]
            vehicles_ids = self.env["fleet.vehicle"].search(
                ['|',('depto_propietario','=',self.departamento_id.id),
                 ('parent_id_department','=',self.departamento_id.id),'&',
                 ('state_id','=','Funcionando'),('fuel_type','=',self.tipo_combustible)])
            for car in vehicles_ids:
                demanda = CombDemanda.sudo().create({
                    'mes_demanda': self.mes_demanda,
                    'estado_demanda': "borrador",
                    'tipo_combustible': self.tipo_combustible,
                    'departamento': self.departamento_id.id,
                    'combustible_tanque': 0,
                    'costo_litro': self.costo_litro,
                    'tipo_demanda': self.tipo_demanda,
                    'vehicle_id': CombDemanda.browse(car.id).id,
                })
                self.demanda_combt_ids |= demanda
        else:
            raise ValidationError("Faltan datos para obtener todas las demandas")


    def do_aprobar_demanda(self):
        if self.demanda_combt_ids:
            return self.write({'estado': 'aprobado'})

    def do_rechazar_demanda(self):
        if self.demanda_combt_ids:
            return self.write({'estado': 'rechazado'})

    def do_rectificar_demanda(self):
        return self.write({'estado': 'demandado'})





