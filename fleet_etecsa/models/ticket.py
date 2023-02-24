# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
import logging
from odoo.exceptions import ValidationError
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

# nomenclador Categoria de Licencia
class fleet_etecsa_ticket(models.Model):
    _name = "fleet.etecsa.ticket"
    _description = "Ticket de Reparación"

    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Número de Reporte", default="CAMBIAR POR NUMERO SAP!")
    # refers_to = fields.Many2one('res.users', string= 'Tecnico de Transporte',)
    stage_fold = fields.Boolean('Stage Folded?', compute='_compute_stage_fold')
    categorie_id = fields.Many2one("fleet.etecsa.ticket.categories", string="Categoría del Problema")
    problems_id = fields.Many2many("fleet.etecsa.ticket.problems", string="Problemas Detectados")
    active = fields.Boolean("Active?", default=True, track_visibility="always")
    fecha_aceptado = fields.Datetime(default=fields.datetime.now(), readonly=True)
    fecha_reportado = fields.Datetime(default=fields.datetime.now(), readonly=True, string = "Fecha Reportado")
    fecha_cierre_ticket = fields.Datetime(string = "Fecha de Cierre")
    create_date = fields.Date(string = "Fecha de Creación")
    tipo_respuesta = fields.Selection([
        ("terceros","Taller de Terceros"),#elegir contrato y proveedores
        ("empresa","Taller de Empresa"),
        ("propio","Medios Propios"),
        ("otros","Otros"),
    ])
    is_telef_reporte = fields.Boolean("Se reportó por Telf?")
    num_telef_reporte = fields.Char("No Telf que reportó")
    state = fields.Selection(
        [('draft', 'Solicitado'), ('open', 'Aceptado'), ('done', 'Resuelto'), ('cancel', 'Cancelado'),
         ('pendent', 'Pendiente')], default='draft', track_visibility="always")
    motivo_pendiente = fields.Text()  # states={state='pendent' visibility=True, required=True}
    actvds_id = fields.One2many("fleet.etecsa.actvds.ticket", "ticket_id", "Actvds del tícket")
    date_start = fields.Datetime("Fecha Apertura tícket")
    date_end = fields.Datetime("Fecha Cierre tícket")
    vehicle_id = fields.Many2one("fleet.vehicle", required=True,string="Vehículo")  # ref a la clase vehiculo
    chofer_id = fields.Many2one(related="vehicle_id.driver_id", readonly=True, string="Chofer")  # ref al chofer del vehiculo
    area_id = fields.Many2one(related="vehicle_id.depto_propietario", readonly=True)  # ref al chofer del vehiculo
    asignado_a = fields.Many2one("res.users",
                domain=lambda self: [("groups_id", "=", self.env.ref("fleet_etecsa.fleet_ticket_tecnico_transporte").id)], string="Responsable")  # tecnico al que esta asignado el vehiculo
    solicitado_por = fields.Many2one("hr.employee", required=True)  # quien solicita el ticket
    description = fields.Text("Descripción")
    proveedor_id = fields.Many2one("res.partner",string="Proveedor Externo (Terceros)",)
    doc_contrato = fields.Binary("Documento del Contrato")

    @api.constrains('state', 'fecha_cierre_ticket', 'vehicle_id')
    def validar_estado_ticket(self):
        if self.vehicle_id:
            Ticket = self.env['fleet.etecsa.ticket']
            listado = Ticket.search_count(
                [('vehicle_id', '=', self.vehicle_id.id), ('state', 'in', ['open', 'draft', 'pendent'])])
            _logger.info('Listado es %s.' % listado)
            if listado > 1:
                raise ValidationError("Existe un Tícket abierto para este Vehículo")

    # Validar que el Ticket no ha sido reportado en 1 semana
    '''
    @api.constrains('vehicle_id', 'fecha_reportado')
    def validar_ticket_semanal(self):
        if self.vehicle_id:
            Ticket = self.env['fleet.etecsa.ticket']
            listado = Ticket.search([('vehicle_id', '=', self.vehicle_id.id)], order='fecha_reportado')
            _logger.info('El listado ordenado es %s.' % listado)
            ultimo = Ticket.browse(listado[-1].id)
            _logger.info('El ultimo elemento  es %s.' % ultimo)
            if ultimo:
                ahora = datetime.now()
                ultima_fecha = ultimo.fecha_reportado
                if ultima_fecha  + timedelta(days=7) > ahora:
                    raise ValidationError("La fecha de solicitud no puede ser mayor que fecha actual")'''



    def do_assign(self):
        self.state = 'open'
    def do_pendent(self):
        self.state = 'pendent'
    def do_cancel(self):
        self.state = 'cancel'
    def do_solve(self):
        self.state = 'done'

class fleet_etecsa_ticket_problem(models.Model):
    _name = "fleet.etecsa.ticket.problems"
    _description = "Tipo de problema Tíckets de Reparación"

    name = fields.Char()
    description = fields.Text()
    task_ids = fields.Many2many('fleet.etecsa.ticket',  # modelo relacionado
                                string='Tasks')


class fleet_etecsa_ticket_categories(models.Model):
    _name = "fleet.etecsa.ticket.categories"
    _description = "Tipo de categoría del Tícket"

    name = fields.Char()
    description = fields.Text("Descripción")
    parent_id = fields.Many2one('fleet.etecsa.ticket.categories', 'Categoria Padre', ondelete='restrict')
    parent_left = fields.Integer('Parent Left', index=True)
    parent_right = fields.Integer('Parent  Right', index=True)
    child_ids = fields.One2many('fleet.etecsa.ticket.categories', 'parent_id', 'Categorias Hijas')


class fleet_etecsa_actividades_ticket(models.Model):
    _name = "fleet.etecsa.actvds.ticket"
    _description = "Actvds del Tícket"
    _order = 'name'

    name = fields.Char("Nombre de la Actividad")
    date_start = fields.Datetime("Fecha Apertura actvd")
    date_end = fields.Datetime("Fecha Cierre actvd")
    doc = fields.Html("Documentos")
    picture = fields.Binary("Imagen Adjunta")
    resultados = fields.Text()
    ticket_id = fields.Many2one('fleet.etecsa.ticket',readonly=True)
    asignado_a = fields.Many2one("hr.employee", string="Responsable")  # empleado al que esta asignado el vehiculo
    participantes = fields.Many2many("hr.employee")










