# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


# plan asignacion de combustible (Modelo Ania Anexo 1)
class fleet_etecsa_vehicle_plan_asign_fuel(models.Model):
    _name = "fleet.etecsa.vehicle.plan.asign.fuel"
    _description = "Plan de Asignacion de combustible"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Plan de Asignacion de combustible")
    asig_comb_ids = fields.One2many("fleet.etecsa.vehicle.asign.fuel","plan_asig_comb_id", "Asignación de Combustible")
    organismo = fields.Char(default="MIC")
    entidad = fields.Char(default="ETECSA")
    u_organizativa = fields.Many2one("hr.department")
    numero_consecutivo_plan = fields.Char(compute='_get_consecutivo', string="Número de Consecutivo del Plan:1",
                                      readonly=True)
    aprobado_por = fields.Char("Aprobado por Vicepresidente VPOR: Ing.Lidia Hidalgo Rodríguez")
    vehicle_id = fields.Many2one("fleet.vehicle")
    chapa = fields.Char(related="vehicle_id.license_plate")
    mes_consumo = fields.Selection([('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
                                    ('5', 'Mayo'), ('6', 'Junio'),('7', 'Julio'), ('8', 'Agosto'),
                                    ('9', 'Septiembre'), ('10', 'Octubre'),('11', 'Noviembre'),
                                    ('12', 'Diciembre')])
    tipo_combustible = fields.Selection([('esp', 'Especial'), ('reg', 'Regular'), ('dies', 'Diesel')])
    concepto_emision = fields.Selection([('opert', 'Plan Operativo'), ('aver', 'Avería'),
                                         ('perd', 'Pérdida'), ('asigad', 'Asignación Adicional'),('resv', 'Reserva')])
    department_id = fields.Many2one("hr.department", string="Depto Responsable")  # depto de la tarjeta
    tarjeta_id = fields.Many2one("fleet.etecsa.tarjeta.combustible", required=True)
    plan_asignado_litros = fields.Float()
    plan_asignado_importe = fields.Float()
    descontar_saldo_existencia = fields.Boolean()
    total_general_plan_distribucion_litros = fields.Float(compute='_get_total_general_plan',string="Total General del Plan de Distribución Litros")
    total_general_plan_distribucion_importe = fields.Float(compute='_get_total_general_plan',string="Total General del Plan de Distribución Importe")
    emergencias = fields.Float(compute='_get_emergencias', string=" Quedarían para Emergencias:")
    observaciones = fields.Float(string="Observaciones")
    nombre_entrega_modelo = fields.Many2one("hr.employee", string="Nombre, Apellidos y firma de quien entrega:")
    nombre_recibe_modelo = fields.Many2one("hr.employee", string="Nombre, apellidos y firma de quien recibe:")
    nombre_jefe_revisado_modelo = fields.Many2one("hr.employee", string="Revisado por Jefe Dpto. de Logística y Servicios:")
    nombre_direc_revisado_modelo = fields.Many2one("hr.employee", string="Visto Bueno por Directora de Logistica y Talleres:")

    active = fields.Boolean("Active?", default=True,track_visibility="always")  # se pone en archivado cuando se entrega el anexo de Liquidacion
    notificar_por_sms = fields.Char()  # ejecutar accion de notificacion x sms
    notificar_por_email = fields.Char()  # ejecutar accion de notificacion x email
    observacion = fields.Text()

    @api.one
    def _get_consecutivo(self):
        last_id = self.env['fleet.etecsa.vehicle.plan.asign.fuel'].search([], order='id desc')[0].id
        if last_id:
            last_id += 1
            self.name = "00%s/2020" % last_id
        else:
            self.name = "001/2020"  # se calcula el Consecutivo

    @api.depends('observaciones', 'total_general_plan_distribucion_litros')
    def _get_emergencias(self):
        if self.observaciones and self.total_general_plan_distribucion_litros:
              self.emergencias = self.observaciones - self.total_general_plan_distribucion_litros  # se calcula  para emergencias

    @api.one
    @api.depends('plan_asignado_importe','plan_asignado_litros')
    def _get_total_general_plan(self):
        if self.plan_asignado_importe:
            self.total_general_plan_distribucion_importe = 0
            for total in self.plan_asignado_importe:
                self.total_general_plan_distribucion_importe += total.liter  # se calcula el total plan_distribucion_importe

        if self.plan_asignado_litros:
            self.total_general_plan_distribucion_litros = 0
            for total in self.plan_asignado_litros:
                self.total_general_plan_distribucion_litros += total.liter  # se calcula el total plan_distribucion_litros



    # cálculo combustible extra (Modelo Solicitud Combustible extra)
class fleet_etecsa_comb_extra_(models.Model):
        _name = "fleet.etecsa.vehicle.comb.extra"
        _description = "Plan de Asignacion de combustible"
        _inherit = ["mail.thread", "mail.activity.mixin"]

        name = fields.Char("Cálculo de Combustible Extra")
        vehicle_id = fields.Many2one("fleet.vehicle")
        u_organizativa = fields.Many2one("hr.department")
        chapa = fields.Char(related="vehicle_id.license_plate")
        tarjeta_id = fields.Many2one("fleet.etecsa.tarjeta.combustible", required=True)
        fecha = fields.Date("Fecha en que se ejecuta la solicitud del Combustible")
        recorridos = fields.Text()
        cant_viajes = fields.Integer()
        km_recorrer = fields.Char("Kilómetros a Recorrer")
        kms_total_recorrido = fields.Float(compute='_get_kms_total_recorrido', string="Kilometraje total recorrido")
        #solicitud_comb = fields.Selection()

        @api.one
        @api.depends('km_recorrer', 'cant_viajes')
        def _get_kms_total_recorrido(self):
            self.kms_total_recorrido = self.km_recorrer * self.cant_viajes


