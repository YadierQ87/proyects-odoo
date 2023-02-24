# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

#registro de licencias de circulacion de vehiculos
class fleet_etecsa_licencia_circulacion(models.Model):
    _name = "fleet.etecsa.licencia.circulacion"
    _description = "Licencia de Circulacion"

    name = fields.Char("Matricula")
    combustible = fields.Char()
    color = fields.Char()
    no_motor = fields.Char()
    no_carroceria = fields.Char()
    foto = fields.Binary()
    fecha_expedicion = fields.Date()
    fecha_vencimiento = fields.Date()
    active = fields.Boolean("Active?", default=True, track_visibility="always")


#certificacion tecnica automotor Somaton
class fleet_etecsa_carnet_revision_tecnica(models.Model):
    _name = "fleet.etecsa.carnet.revision.tecnica"
    _description = "somaton del vehiculo"

    name = fields.Char("Numero de Informe de Revision")
    matricula = fields.Char()
    color = fields.Char()
    clasificacion = fields.Char()
    marca_modelo = fields.Char()
    foto = fields.Binary()
    fecha_expedicion = fields.Date()
    fecha_vencimiento = fields.Date()
    active = fields.Boolean("Active?", default=True, track_visibility="always")


#clase que hereda de vehiculo y lo modifica
class fleet_etecsa_vehicle(models.Model):
    _name = "fleet.vehicle"
    _inherit = ["fleet.vehicle"] #heredando y sobreescribiendo metodos o atributos

    odometro_funcionando = fields.Boolean()
    ticket_ids = fields.One2many("fleet.etecsa.ticket","vehicle_id");
    asignado_a = fields.Many2one("hr.employee") #empleado al que esta asignado el vehiculo
    chofer = fields.Many2one("fleet.etecsa.chofer")#chofer al que esta asignado el vehiculo
    chofer_nombre = fields.Char("Asignacion")#nombre del chofer
    depto_propietario = fields.Many2one("hr.department") #departamento al que esta asignado el vehiculo
    lic_circulacion_id = fields.Many2one("fleet.etecsa.licencia.circulacion")#lic de circulacion activa
    carnet_somaton_id = fields.Many2one("fleet.etecsa.carnet.revision.tecnica")#carne somaton activa
    asign_fuel_ids = fields.One2many("fleet.etecsa.vehicle.asign.fuel","vehicle_id",
                                     "Asignación de Combustible")  # list asignacion comb
    anexo_unico_ids = fields.One2many("fleet.etecsa.anexo.unico","vehicle_id","Anexo Unico")#list anexo unicomm  cbb
    anexo_liquidacion_ids = fields.One2many("fleet.etecsa.anexo.liquidacion","vehicle_id","Anexo 5 Liquidacion Combustible")#list anexo unico
    estado_chapisteria = fields.Selection([("e","Excelente"),("b","Bueno"),("r","Regular"),("m","Malo"),("p","Pésimo")])
    estado_general = fields.Selection([("e","Excelente"),("b","Bueno"),("r","Regular"),("m","Malo"),("p","Pésimo")])
    #contadores
    anexo_unico_count = fields.Integer(compute="_compute_count_combustible", string='Services')
    anexo_liquidacion_count = fields.Integer(compute="_compute_count_combustible", string='Services')
    fecha_dia_tecnica = fields.Date(string = "Fecha Dia Tecnica")
    observacion_dia_tecnica = fields.Text(string = "Observaciones")
    foto_tecnica = fields.Binary()
    tipo_ring = fields.Char( string ="Tipo de Ring")
    modelo = fields.Char( string ="Modelo del Vehiculo")
    model_id = fields.Many2one('fleet.vehicle.model', 'Model',
                               track_visibility="onchange", required=False, help='Model of the vehicle')
    clasificacion_ring = fields.Char( string ="Clasificación de Ring")
    #nuevos atributos del motor
    vin = fields.Char( string ="VIN")
    no_serie = fields.Char( string ="No de Serie")
    no_inventario = fields.Char( string ="No de Inventario")
    no_motor = fields.Char( string ="No de Motor")
    no_circulacion = fields.Char( string ="No de Circulacion")
    tipo_auto = fields.Char( string ="Tipo de auto")
    actividad = fields.Char( string ="Actividad")#operacion
    jefe = fields.Char( string ="Jefe del Conductor")
    codigo = fields.Char( string ="codigo")
    anno_fabricacion = fields.Char( string ="Año de fabricacion")

    _sql_constraints = [
        ('lic_circulacion_id_uniq','UNIQUE (id, lic_circulacion_id)','Licencia de Circulación must be unique!'),
        ('carnet_somaton_id_uniq','UNIQUE (id, carnet_somaton_id)','Carnet de Revision Técnica must be unique!'),
    ]

    def _compute_count_combustible(self):
        AnexoUnico = self.env['fleet.etecsa.anexo.unico']
        AnexoLiquidacion = self.env['fleet.etecsa.anexo.liquidacion']
        for record in self:
            record.anexo_unico_count = AnexoUnico.search_count([('vehicle_id', '=', record.id)])
            record.anexo_liquidacion_count = AnexoLiquidacion.search_count([('vehicle_id', '=', record.id)])

    @api.multi
    def return_action_comb_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window'].for_xml_id('fleet_etecsa', xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('vehicle_id', '=', self.id)]
            )
            return res
        return False
