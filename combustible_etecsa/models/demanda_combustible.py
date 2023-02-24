# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class CombEtecsaDemandaCombustible(models.Model):
    _name = "comb.etecsa.demanda.combustible"
    _description = "Modelo Demanda Combustible"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Modelo Demanda Combustible", readonly=True, required=True, copy=False, default='New',
                       order="desc")
    vehicle_id = fields.Many2one("fleet.vehicle")
    demanda_departamento_id = fields.Many2one("comb.etecsa.demanda.departamento")
    chapa = fields.Char(related="vehicle_id.license_plate",
                        string="Chapa", store=True)
    tarjeta = fields.Char(related="vehicle_id.tarjeta",
                        string="Tarjeta Combustible", store=True)
    u_organizativa = fields.Char(default="VPOR")
    departamento = fields.Many2one(related="vehicle_id.depto_propietario",
                                   store=True, string="Departamento")
    asignado_a = fields.Many2one(related="vehicle_id.asignado_a",
                                 store=True, string="Asignado a:")
    estado_chapisteria = fields.Selection(related="vehicle_id.estado_chapisteria",
                                          store=True, string="Estado del Vehículo:")
    mes_demanda = fields.Selection([('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
                                    ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
                                    ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
                                    ('12', 'Diciembre')],required=True)
    tipo_combustible = fields.Selection(related="vehicle_id.fuel_type", store=True, string="Tipo Combustible")
    indice_consumo = fields.Float(related="vehicle_id.indice_consumo", store=True, string="Índice Consumo:")
    combustible_tanque = fields.Float(string="Combustible en Tanque",required=True)
    prioridad = fields.Selection(related='vehicle_id.prioridad')
    estado_demanda = fields.Selection(
        [('borrador', 'Borrador'),
         ('demandado', 'Demandado'),
         ('aprobado', 'Aprobado'),
         ('asignado', 'Asignado'),
         ('rechazado', 'Rechazado')],
        string="Estado de la Demanda", default="borrador")
    total_demanda = fields.Float(compute="_get_total_valores", string="Total demanda")#Se calcula segun los recorridos
    ult_km_recorridos = fields.Float(string="Los km recorridos del mes anterior",help="Poner la cantd de km recorridos en el ultimo mes")#Se calcula segun los recorridos
    combustible_demandado = fields.Float(string="Combustible Demandado")#se calcula en base a lo propuesta por el recorrido pero lo puede modificar el jefe
    combustible_real = fields.Float(string="Combustible Real Asignado")#el combustible real que se asigno a esa demanda (se asigna en el paso final)
    comb_demanda_x_prio = fields.Float(compute="_compute_demanda_x_prio",string="Combustible Calculado x Prioridad")#demanda_x_prio = (demanda.combustible_demandado * prioridad) / maximo_prioridad
    active = fields.Boolean("Active?", default=True,
                            track_visibility="always")  # se pone en archivado cuando se entrega el anexo
    total_km = fields.Float(compute="_get_total_valores",
                            string="Total de Kilómetros")
    observaciones = fields.Text(string="Observaciones")
    costo_litro = fields.Float("Costo del Litro")
    importe = fields.Float("Importe", compute="_get_importe_combustible")
    demanda_recorridos_ids = fields.One2many("comb.etecsa.recorridos.combustible", "demanda_comb_id", "Recorridos",required=True)
    demanda_dpto_id = fields.Many2one("comb.etecsa.demanda.departamento",ondelete='cascade')
    tipo_demanda = fields.Selection(
        [('normal', 'normal'),
         ('segunda-vuelta', 'segunda-vuelta'),
         ('demanda-extra', 'demanda-extra'),
         ('emergencia', 'emergencia'),],
        string="Tipo de la Demanda", default="normal")

    _sql_constraints = [
        ('demanda_comb_name_uniq',
         'UNIQUE (tipo_demanda, vehicle_id,mes_demanda)',
         'Solo puede existir un tipo de demanda por vehiculo por mes!')]


    @api.depends('costo_litro','combustible_real')
    def _get_importe_combustible(self):
        for demanda in self:
            if demanda.costo_litro and demanda.costo_litro > 0:
                if demanda.combustible_real and demanda.combustible_real > 0:
                    demanda.importe = demanda.combustible_real * demanda.costo_litro
            else:
                demanda.importe = 0.00

    @api.depends('total_demanda', 'combustible_demandado','demanda_recorridos_ids')
    def _chequear_datos_distribucion(self):
        if self.vehicle_id:
            Demanda = self.env['comb.etecsa.demanda.combustible']
            listado = Demanda.search_count(
                [('vehicle_id', '=', self.vehicle_id.id), ('state', 'in', ['demandado', 'aprobado', 'rechazado'])])
            if listado > 1:
                raise ValidationError("Existe una Demanda abierta para este Vehículo")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('comb.etecsa.demanda.combustible.die') or 'New'
        result = super(CombEtecsaDemandaCombustible, self).create(vals)
        return result


    @api.depends('combustible_demandado')
    def _compute_demanda_x_prio(self):
        maximo_prioridad = 6
        for item in self:
            prioridad = int(item.prioridad)
            item.comb_demanda_x_prio = ((item.combustible_demandado - item.combustible_tanque) * prioridad) / maximo_prioridad


    @api.multi
    @api.depends('demanda_recorridos_ids')
    def _get_total_valores(self):
        # This will make sure we have on record, not multiple records.
        for demanda in self:
            total_km = total_demanda = 0
            if demanda.demanda_recorridos_ids:
                for recorrido in demanda.demanda_recorridos_ids:
                    total_km += recorrido.km_total_recorrido
                    total_demanda += recorrido.cantd_litros
            demanda.total_demanda = total_demanda
            demanda.total_km = total_km

    #cambiar los estados
    def do_check(self):
        return self.write({'estado_demanda': 'aprobado'})

    def do_failed(self):
        return self.write({'estado_demanda': 'rechazado'})

    def do_rectificar_demanda(self):
        return self.write({'estado_demanda': 'demandado'})

    def do_presentar_demanda(self):
        return self.write({'estado_demanda': 'demandado'})


   

