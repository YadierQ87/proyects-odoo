# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CombEtecsaDistribucion(models.Model):
    _name = "comb.etecsa.distribucion"
    _description = "Modelo Combustible"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Plan de Asignacion de combustible",readonly=True, required=True, copy=False, default='New',)
    organismo = fields.Char(default="MINCOM")
    entidad = fields.Char(default="ETECSA")
    u_organizativa = fields.Char(default="VPOR")
    area_trabajo = fields.Many2one("hr.department")
    numero_consecutivo_plan = fields.Char(string="Número de Consecutivo del Plan:",
                                          readonly=True,
                                          required=True,
                                          copy=False,
                                          default='New', order="desc")
    aprobado_por = fields.Many2one("hr.employee", string="Aprobado por:")
    mes_consumo = fields.Selection([('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
                                    ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
                                    ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
                                    ('12', 'Diciembre')],required=True)
    tipo_combustible = fields.Selection([("Diesel", "Diesel"), ("Gasolina Especial", "Gasolina Especial"), ("Gasolina Regular", "Gasolina Regular")],required=True)
    concepto_emision = fields.Selection([('operativo', 'Plan Operativo'), ('averria', 'Avería'),
                                         ('perdida', 'Pérdida'), ('adicional', 'Asignación Adicional'), ('reserva', 'Reserva')])
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('demandado', 'Demandado'),
        ('asignado', 'Asignado'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado')],
        string="Estado Demanda por Dpto.", default="demandado")
    descontar_saldo_existencia = fields.Boolean()
    costo_litro = fields.Float(compute="_get_costo_litro")
    litros_asignados = fields.Float(required=True)#requerido
    total_litros = fields.Float(compute="_compute_totales",string="Total General del Plan de Distribución Litros")
    total_lts_demandado = fields.Float(compute="_compute_totales",string="Total Litros Demandados")
    total_lts_asignado = fields.Float(compute="_compute_totales",string="Total Litros Distribuidos")#distribuidos
    total_demanda_x_prio = fields.Float(compute="_compute_totales",string="Demandados x Prioridad")
    total_importe = fields.Float(compute="_compute_totales",string="Importe Total")
    emergencias = fields.Float( string=" Reserva para Emergencias:")
    observaciones = fields.Float(string="Observaciones")
    nombre_entrega_modelo = fields.Many2one("hr.employee", string="Nombre, Apellidos de quien entrega:")
    nombre_recibe_modelo = fields.Many2one("hr.employee", string="Nombre, apellidos de quien recibe:")
    nombre_jefe_revisado_modelo = fields.Many2one("hr.employee", string="Revisado por :")
    nombre_direc_revisado_modelo = fields.Many2one("hr.employee", string="Visto Bueno por :")
    state = fields.Selection([('nuevo', 'nuevo'), ('aprobado', 'aprobado'), ('cerrado', 'cerrado')])
    active = fields.Boolean("Active?", default=True,
                            track_visibility="always")  # se pone en archivado cuando se entrega el anexo de Liquidacion
    observacion = fields.Text()
    demanda_combt_ids = fields.Many2many("comb.etecsa.demanda.combustible",string="Demandas")


    def do_listar_demandas_depto(self):
        if self.tipo_combustible and self.mes_consumo and self.litros_asignados:
            #todas las demandas aprobadas
            self.demanda_combt_ids = self.env["comb.etecsa.demanda.combustible"].search([
                ('mes_demanda','=',self.mes_consumo),
                ('estado_demanda','=',"aprobado"),
                ('tipo_combustible','=',self.tipo_combustible),
            ])
        else:
            raise ValidationError("Faltan datos para obtener todas las demandas")

    #sugerencia de asignacion automatica de combustible
    def do_asignar_combustible(self):
        if self.demanda_combt_ids:
            for demanda in self.demanda_combt_ids:
                if self.litros_asignados > 0:
                    percent_demanda_prio = (demanda.comb_demanda_x_prio * 100)/self.total_demanda_x_prio
                    asignacion_lts = (self.litros_asignados * percent_demanda_prio)/100
                    demanda.combustible_real = asignacion_lts

    #aprobar y cerrar la distribucion para poder imprimir el doc
    def do_aprobar_demanda(self):
        if self.demanda_combt_ids:
            for demanda in self.demanda_combt_ids:
                demanda.estado_demanda = "asignado"
            return self.write({'estado': 'aprobado'})


    # @api.constrains('total_lts_asignado')
    # def _chequear_datos_distribucion(self):
    #     if self.total_lts_asignado > self.litros_asignados:
    #         raise ValidationError(
    #             "La suma total de combustible asignado no puede ser mayor que la cantd de litros asignados: %s" % self.litros_asignados)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('comb.etecsa.distribucion.combustible.consec') or 'New'
        return super(CombEtecsaDistribucion, self).create(vals)


    def do_rectificar_demanda(self):
        if self.demanda_combt_ids:
            return self.write({'estado': 'borrador'})

    @api.depends('tipo_combustible')
    def _get_costo_litro(self):
        if self.tipo_combustible:
            self.costo_litro = self.env["comb.costo.litro"].search(
                [('tipo_combustible', '=', self.tipo_combustible)]).costo
        else:
            self.costo_litro = 0.00

    @api.depends('demanda_combt_ids')
    def _compute_totales(self):
        if self.demanda_combt_ids:
            total_lts_demandado = demanda_x_prio = total_lts_asignado = importe = 0
            for demanda in self.demanda_combt_ids:
                total_lts_demandado += demanda.combustible_demandado
                demanda_x_prio += demanda.comb_demanda_x_prio
                total_lts_asignado += demanda.combustible_real
                importe += demanda.importe
            self.total_lts_demandado = total_lts_demandado
            self.total_demanda_x_prio = demanda_x_prio
            self.total_lts_asignado = total_lts_asignado #distribuidos
            self.total_importe = importe
            self.total_litros = self.total_lts_asignado + self.emergencias
            if round(self.total_litros,2) > round(self.litros_asignados,2):
                raise ValidationError(
                    "La suma total de combustible %s no puede ser mayor que la cantd de litros asignados: %s" % (self.total_litros,self.litros_asignados))








