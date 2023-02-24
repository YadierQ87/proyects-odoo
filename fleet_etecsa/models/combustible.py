# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

today = datetime.today().strftime("%d/%m/%Y")
# asignacion de combustible [Esp de Economia] carga de la tarjeta
class fleet_etecsa_vehicle_asign_fuel(models.Model):
    _name = "fleet.etecsa.vehicle.asign.fuel"
    _description = "Asignacion de combustible"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    vehicle_id = fields.Many2one("fleet.vehicle")
    fecha_asignacion = fields.Date(default=fields.Date.today())
    mes_curso = fields.Selection(
        [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
         ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Septiembre'), ('10', 'Octubre'),
         ('11', 'Noviembre'), ('12', 'Diciembre'),
         ])
    cantidad_litros = fields.Float()
    centro_costo = fields.Char()
    observaciones = fields.Text()
    active = fields.Boolean("Active?", default=True,
                            track_visibility="always")  # se pone en archivado cuando se entrega el anexo de Liquidacion
    fecha_cierre = fields.Date("Fecha de Entrega de Anexo Liquidacion")
    anexo_liquidacion = fields.Many2one("fleet.etecsa.anexo.liquidacion")
    tarjeta_id = fields.Many2one("fleet.etecsa.tarjeta.combustible")
    notificar_por_sms = fields.Char()  # ejecutar accion de notificacion x sms
    notificar_por_email = fields.Char()  # ejecutar accion de notificacion x email


# --- Clases para los modelos y anexos a entregar x los choferes ----
class fleet_etecsa_tarjeta_combustible(models.Model):
    _name = "fleet.etecsa.tarjeta.combustible"
    _description = "Tarjeta de combustible"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("No Tarjeta", required=True)
    responsable_id = fields.Many2one("hr.employee", string="Responsable de la Tarjeta",
                                     domain="[('department_id', '=',department_id)]")  # responsable de la tarjeta
    vehicle_id = fields.Many2one("fleet.vehicle", "Vehículo asignado")
    department_id = fields.Many2one("hr.department", string="Depto Responsable")  # depto de la tarjeta
    tipo_combustible = fields.Selection([('esp', 'Especial'), ('reg', 'Regular'), ('dies', 'Diesel')])
    asign_fuel_ids = fields.One2many("fleet.etecsa.vehicle.asign.fuel", "tarjeta_id",
                                     "Asignación de Combustible")  # list asignacion comb
    active = fields.Boolean("Active?", default=True, track_visibility="always")
    pin = fields.Char()

    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current tarjeta """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window'].for_xml_id('fleet_etecsa', xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('tarjeta_id', '=', self.id)]
            )
            return res
        return False

# subclass Serviciado de combustible Cada vez que se echa combustible a un vehiculo
class fleet_etecsa_servicio_combustible(models.Model):
    _name = "fleet.vehicle.log.fuel"
    _description = "Servicio de combustible"
    _inherit = ["fleet.vehicle.log.fuel"]
    _order = 'date'

    tarjeta_id = fields.Many2one("fleet.etecsa.tarjeta.combustible", required=True)
    anexo_unico_id = fields.Many2one("fleet.etecsa.anexo.unico")
    tipo_combustible_ref = fields.Selection(related="tarjeta_id.tipo_combustible", readonly=True)
    combustible_en_tanque = fields.Float()


# anexo unico de combustible [Lo crea el chofer registrado]
class fleet_etecsa_anexo_unico(models.Model):
    _name = "fleet.etecsa.anexo.unico"
    _description = "Anexo unico combustible"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    vehicle_id = fields.Many2one("fleet.vehicle", required=True)  # ref a la clase vehiculo
    chapa = fields.Char(related="vehicle_id.license_plate")
    date_create = fields.Date()
    entidad = fields.Char(default="ETECSA")
    oace = fields.Char("OACE", default="MIC")
    habilitado_por = fields.Reference([('res.users', 'Usuario Odoo'),('hr.employee', 'Empleado')], 'Habilitado por:',required=True) # tecnico de transporte
    km_inicial = fields.Float("Kilometraje Inicial", required=True)
    km_prox_mtto = fields.Float("Km próximo Mtto")  # lo llena el tecnico de transporte
    comb_estimado_tanq = fields.Float("Combustible estimado en tanque")
    indice_consumo = fields.Float("Índice de consumo", required=True)
    active = fields.Boolean("Active?", default=True, track_visibility="always")
    servicio_combustible_id = fields.One2many("fleet.vehicle.log.fuel",'anexo_unico_id')  # listado de Serviciados de combustible
    observaciones = fields.Text()
    # campos calculados
    km_final = fields.Float("Kilometraje final", required=True)
    comb_tanque = fields.Float("Combustible en tanque")
    km_total_recorrido = fields.Float(compute='_get_km_total_recorrido', string="Kilometraje total recorrido")
    comb_total_consumido = fields.Float(compute='_get_total_combustible', readonly=True, store=True, default=0,
                                        string="Combustible total consumido")
    comb_total_serviciado = fields.Float(compute='_get_total_combustible', readonly=True, store=True, default=0,
                                         string="Combustible total Serviciado")
    plan_comb = fields.Float(compute='_get_plan_real_percent', string="Plan")
    percent_plan_real = fields.Float(compute='_get_plan_real_percent', string="Real / Plan %")
    # datos de Mantenimiento
    tipo_mtto = fields.Char("Tipo de Mtto.")
    km_real_mtto = fields.Float("Kilometraje real")
    variacion = fields.Char("Variación")
    #serv_comb_count = fields.Integer(compute="_compute_cantd_combustible", string='Services')#Cantd de Veces Serviciados

    _sql_constraints = [
        ('servicio_combutible_id_uniq', 'UNIQUE (id, servicio_combustible_id)',
         'El Servicio de Combustible  solo puede estar asociado a un Anexo!' )
    ]

    @api.one
    @api.depends('servicio_combustible_id', 'comb_tanque', 'comb_estimado_tanq')
    def _get_total_combustible(self):
        if self.servicio_combustible_id:
            self.comb_total_serviciado = 0
            for servicio in self.servicio_combustible_id:
                self.comb_total_serviciado += servicio.liter  # se calcula el total serviciado
            self.comb_total_consumido = self.comb_estimado_tanq + self.comb_total_serviciado - self.comb_tanque

    @api.one
    @api.depends('km_final', 'km_inicial')
    def _get_km_total_recorrido(self):
        self.km_total_recorrido = self.km_final - self.km_inicial

    @api.one
    @api.depends('comb_total_consumido', 'km_total_recorrido')
    def _get_plan_real_percent(self):
        if self.km_total_recorrido > 0 and self.comb_total_consumido > 0:
            self.plan_comb = self.km_total_recorrido / self.comb_total_consumido
            self.percent_plan_real = self.plan_comb * 100 / self.indice_consumo

    @api.one
    @api.constrains('servicio_combustible_id')
    def _check_km_recorridos_servicio(self):
        if self.servicio_combustible_id:
            for services in self.servicio_combustible_id:
                if services.odometer <= self.km_inicial or services.odometer >= self.km_final:
                    raise ValidationError('Existen errores entr las distancia final y de los servicios! %s ' % services.odometer)


# anexo 5 liquidacion del combustible
# ANEXO 5  de la IC-026-2012- Modelos Modificados
class fleet_etecsa_anexo_liquidacion(models.Model):
    _name = "fleet.etecsa.anexo.liquidacion"
    _description = "Anexo liquidacion combustible"
    _inherit = ["mail.thread", "mail.activity.mixin"]


    tipo_elemento = fields.Selection([
        ("vehicle", "Vehículo:"), ("electrogeno", "Grupo Electrógeno"), ("camion", "Camión Cisterna"),
        ("equipo", "Equipo especial construcción"), ("herramienta", "Herramienta Operaciones"),
        ("otro", "Otros")], string="Elemento que requiere el combustible")
    organismo = fields.Char(default="MIC")
    entidad = fields.Char(default="ETECSA")
    vehicle_id = fields.Many2one("fleet.vehicle", string="Chapa del Vehiculo Etecsa")  # ref a la clase vehiculo
    depto_propietario = fields.Many2one(related="vehicle_id.depto_propietario",
                                        string="Area de Trabajo")  # departamento al que esta asignado el vehiculo
    chapa = fields.Char(related="vehicle_id.license_plate",readonly=True)
    tool_id = fields.Many2one("maintenance.equipment", string="Equipo")  # ref a la clase vehiculo
    centro_costo = fields.Char(related="depto_propietario.centro_costo_mlc")
    tarjeta_id = fields.Many2one("fleet.etecsa.tarjeta.combustible")
    tipo_combustible = fields.Selection(related="tarjeta_id.tipo_combustible",readonly=True)
    # Operaciones Tarjeta Consumo
    #saldo_ini_nombre = fields.Char(string="Saldo inicial de la tarjeta")
    saldo_ini_importe = fields.Float(string="Importe")
    saldo_ini_moneda =  fields.Selection([('CUP', 'CUP'), ('CUC', 'CUC'), ('MLC', 'MLC')],default="CUC")
    saldo_ini_cantdlts = fields.Float(string="Cantd Lts")
    #comb_consumido_nombre = fields.Char(string="Combustible consumido de la tarjeta")
    comb_consumido_importe = fields.Float(string="Importe")
    comb_consumido_moneda = fields.Selection([('CUP', 'CUP'), ('CUC', 'CUC'), ('MLC', 'MLC')],default="CUC")
    comb_consumido_cantdlts = fields.Float(string="Cantd Lts")
    #saldo_final_nombre = fields.Char(string="Saldo final de la tarjeta")
    saldo_final_importe = fields.Float(string="Importe")
    saldo_final_moneda =  fields.Selection([('CUP', 'CUP'), ('CUC', 'CUC'), ('MLC', 'MLC')],default="CUC")
    saldo_final_cantdlts = fields.Float(string="Cantd Lts")
    cantd_comprobantes = fields.Integer("Cantidad de Comprobantes")
    desglose = fields.Char("Desglose del consumo de la tarjeta")  # array de num separados x lista
    #gastos_oper_nombre = fields.Char(string="Gastos de la Operación")
    gastos_oper_importe = fields.Float(string="Importe")
    gastos_oper_moneda =  fields.Selection([('CUP', 'CUP'), ('CUC', 'CUC'), ('MLC', 'MLC')],default="CUC")
    gastos_oper_cantdlts = fields.Float(string="Cantd Lts")
    #gastos_eventos_nombre = fields.Char(string="Gastos por eventos del Seguro")
    gastos_eventos_importe = fields.Float(string="Importe")
    gastos_eventos_moneda = fields.Selection([('CUP', 'CUP'), ('CUC', 'CUC'), ('MLC', 'MLC')],default="CUC")
    gastos_eventos_cantdlts = fields.Float(string="Cantd Lts")
    #gastos_inversiones_nombre = fields.Char(string="Gastos de Inversiones")
    gastos_inversiones_importe = fields.Float(string="Importe")
    gastos_inversiones_moneda = fields.Selection([('CUP', 'CUP'), ('CUC', 'CUC'), ('MLC', 'MLC')],default="CUC")
    gastos_inversiones_cantdlts = fields.Float(string="Cantd Lts")
    active = fields.Boolean("Active?", default=True, track_visibility="always")
    # Otros indicadores
    no_elem_pep = fields.Char("No. Elemento PEP")
    importe_elem_pep = fields.Float("Importe Elemento PEP")
    const_montaje = fields.Float("Componentes: Const. y Montaje")
    project = fields.Char("Proyecto")
    otros_gastos = fields.Float("Otros gastos")
    no_orden_trabajo = fields.Char("No. Orden de Trabajo")  # se puede relacionar con una orden de trabajo
    # elementos finales Nombres  y Economia
    nombre_elabora_modelo = fields.Many2one("hr.employee", "Nombre de quien elabora el modelo de Liquidación")
    nombre_jefe_aprueba = fields.Many2one("hr.employee", "Nombre del Jefe administrativo que aprueba la Liquidación")
    nombre_quien_liquida = fields.Many2one("hr.employee", "Nombre de quien liquida  la tarjeta en la Caja")
    fecha_liquidacion_caja = fields.Date("Fecha en que se ejecuta la liquidación en la Caja")
    nombre_cajero_recibe_liq = fields.Many2one("hr.employee", "Nombre del cajero que recibe la liquidación")
    nombre_contador_registra_liq = fields.Many2one("hr.employee", "Nombre del Contador que registra la liquidación")
    comprobado = fields.Boolean(compute='_check_values_anexo',default=False,string="Validado?")


    @api.one
    @api.constrains(
        'saldo_ini_importe', 'saldo_ini_cantdlts',
        'saldo_final_importe','saldo_final_cantdlts',
        'comb_consumido_importe', 'comb_consumido_cantdlts',
        'desglose','cantd_comprobantes',
        'gastos_oper_importe', 'gastos_oper_cantdlts',
        )
    def _check_values_anexo(self):
        if float(self.saldo_ini_importe) == 0 and float(self.saldo_ini_cantdlts) == 0:  # no hubo asignacion
            if float(self.saldo_final_cantdlts) > 0:
                raise ValidationError('Error en saldo_final_cantdlts pk no existe asignacion')
            if float(self.saldo_final_importe) > 0:
                raise ValidationError('Error en saldo_final_importe pk no existe asignacion')
            if float(self.comb_consumido_importe) > 0:
                raise ValidationError('Error en comb_consumido_importe pk no existe asignacion')
            if float(self.comb_consumido_cantdlts) > 0:
                raise ValidationError('Error en comb_consumido_cantdlts pk no existe asignacion')
            if float(self.gastos_oper_importe) > 0:
                raise ValidationError('Error en gastos_oper_importe pk no existe asignacion')
            if float(self.gastos_oper_cantdlts) > 0:
                raise ValidationError('Error en gastos_oper_cantdlts pk no existe asignacion')
            if float(self.cantd_comprobantes) > 0:
                raise ValidationError('Error en cantd_comprobantes pk no existe asignacion')
            if self.desglose != "" and self.desglose:
                raise ValidationError('Error en desglose pk no existe asignacion')
        if float(self.saldo_ini_importe) > 0 and float(self.saldo_ini_cantdlts) == 0:  # si hubo asignacion
            raise ValidationError(
                'Si existe importe %s ,la cants de litros inicial  no puede ser cero!' % self.saldo_ini_importe)
        if float(self.saldo_ini_importe) <= 0 and float(self.saldo_ini_cantdlts) > 0:  # si hubo asignacion
            raise ValidationError(
                'Si existe cantd de litros %s ,el importe inicial  no puede ser cero!' % self.saldo_ini_cantdlts)
        if float(self.saldo_ini_importe) > 0 and float(self.saldo_ini_cantdlts) > 0:  # si hubo asignacion
            if float(self.saldo_final_importe) != float(self.saldo_ini_importe) and float(self.saldo_final_cantdlts) != float(self.saldo_ini_cantdlts):  # si hubo gastos
                if float(self.saldo_final_cantdlts) > float(self.saldo_ini_cantdlts):
                    raise ValidationError("La cants de litros final %s no puede ser mayor que la asignada!" % self.saldo_final_cantdlts)
                if float(self.saldo_final_importe) > float(self.saldo_ini_importe):
                    raise ValidationError(
                        "El saldo final %s no puede ser mayor que el importe asignado!" % self.saldo_final_importe)
                if float(self.comb_consumido_importe) != float(self.gastos_oper_importe):
                    raise ValidationError(
                        "Gastos de Operacion tienen que ser igual al importe consumido!")
                if float(self.comb_consumido_cantdlts) != float(self.gastos_oper_cantdlts):
                    raise ValidationError(
                        "Litros de Operacion tienen que ser igual al importe de consumido!")
                if float(self.saldo_final_importe) != float(self.saldo_ini_importe) - float(self.comb_consumido_importe):
                    raise ValidationError(
                        "Cantd de lts final no puede ser %s !" % self.saldo_final_cantdlts)
                if float(self.saldo_final_importe) > 0 and float(self.saldo_final_cantdlts) <= 0:
                    raise ValidationError(
                        "Saldo final no coincide con la diferencia del importe consumido y el saldo inicial!")
                if float(self.saldo_final_cantdlts) != 0 and float(self.comb_consumido_cantdlts) != 0:
                    if float(self.saldo_final_cantdlts) != float(self.saldo_ini_cantdlts) - float(self.comb_consumido_cantdlts):
                        raise ValidationError(
                            "Saldo final litros no coincide con la diferencia de los litros consumidos y el combustible inicial!")
                # cantd de comprobantes tiene que ser igual a la sumatoria del desglose de consumo separado x comas
                if self.desglose and self.cantd_comprobantes:
                    comprobantes = self.desglose.split(',')
                    sum = 0
                    max = len(comprobantes)
                    for tiket in comprobantes:
                        sum += int(tiket)
                    if max != float(self.cantd_comprobantes):
                        raise ValidationError(
                            'El desglose debe coincidir con la cantd de comprobantes!')
                    if float(self.comb_consumido_cantdlts) != float(sum):
                        raise ValidationError(
                            'Combustible consumido no coincide con la sumatoria del desglose %s!' % sum)
            self.comprobado = True



