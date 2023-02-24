# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from datetime import datetime
from odoo.exceptions import ValidationError

class Followers(models.Model):
    _inherit = 'mail.followers'

    @api.model
    def create(self, vals):
        if 'res_model' in vals and 'res_id' in vals and 'partner_id' in vals:
            dups = self.env['mail.followers'].search([('res_model', '=',vals.get('res_model')),
                                           ('res_id', '=', vals.get('res_id')),
                                           ('partner_id', '=', vals.get('partner_id'))])
            if len(dups):
                for p in dups:
                    p.unlink()
        res = super(Followers, self).create(vals)
        return res

class ProductoGenerico(models.Model):
    _name = "demanda.producto.generico.logistica"
    _description = 'Producto Generico de Logistica'  # agregado

    name = fields.Char("Nombre Generico del Producto",required=True)
    descripcion = fields.Char("Descripcion del Producto")
    cantds_solicitar = fields.Char("Cantds a Solicitar")
    no_sap = fields.Char("Numero en SAP")
    categoria = fields.Selection([("inmueble","inmueble"),("insumo","insumo"),("herramienta","herramienta"),
                                  ("otros","otros")])
    solicitud_id = fields.Many2one("demanda.solicitud.generica")  # Asociado a solicitud

#Es la Planilla de Captación de Datos
class SolicitudGenerica(models.Model):
    _name = "demanda.solicitud.generica" #cambiado uniforme
    _description = 'Planilla de Captación Demanda Generica'  # agregado
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(compute='_compute_solicitud_name', readonly=True)
    trabajador_id = fields.Many2one("hr.employee",string="Nombre trabajador")
    plantilla_logistica_id = fields.Many2one("demanda.plantilla.logistica")  # Tipo de Plantilla
    sexo_worker = fields.Char(compute='_compute_get_worker',string="Sexo")#"trabajador_id.gender.name"
    depto_worker = fields.Char(compute='_compute_get_worker',string="Departamento")#"trabajador_id.department_id.name"
    jefe_worker = fields.Char(compute='_compute_get_worker',string="Jefe Depto.")#"trabajador_id.department_id.manager_id.name"
    active = fields.Boolean("Active?", default=True,track_visibility="always")
    categoria_demanda = fields.Selection([("inmueble","Inmueble"),("insumo","Insumo"),("herramienta","Herramienta"),
                                  ("otros","Otros")])
    presupuesto = fields.Selection([("Operaciones","Operaciones"),("Inversiones","Inversiones")])
    centro_costo = fields.Char()
    cuenta_gasto = fields.Char()
    existencia_recurso_almacen = fields.Boolean()
    no_solicitud_sap = fields.Char()
    proveedor = fields.Char()
    especificaciones_tecnicas = fields.Text()
    si_procede = fields.Boolean()
    Observaciones = fields.Text()
    producto_generico_ids = fields.One2many("demanda.producto.generico.logistica","solicitud_id")#Lista de Tuplas Producto Atributos
    vista_previa = fields.Html(compute="_get_plantilla_html",store=False)


    @api.one
    @api.depends('trabajador_id')
    def _compute_solicitud_name(self):
        today = datetime.today().strftime("%d/%m/%Y")
        if self.trabajador_id and self.depto_worker:
            self.name = 'Demanda del %s por %s fecha %s' % (self.depto_worker, self.trabajador_id.name, today)
        elif self.trabajador_id and self.categoria:
            self.name = 'Demanda del %s por %s fecha %s' % (self.categoria, self.trabajador_id.name, today)

    @api.one
    @api.depends('trabajador_id')
    def _compute_get_worker(self):
        if self.trabajador_id:
            jefe = "-- no esta definido --"
            depto = "-- no esta definido --"
            if self.trabajador_id.department_id:
                department = self.trabajador_id.department_id
                depto = self.env['hr.department'].browse(department.id).name
            if department.manager_id:
                jefe = self.env['hr.employee'].browse(department.manager_id.id).name
            self.sexo_worker = self.trabajador_id.gender
            self.depto_worker = depto
            self.jefe_worker = jefe


    @api.one
    @api.depends('producto_generico_ids')
    def _get_plantilla_html(self):
        table_html = "<table class='table table-bordered table-hover'>"
        if self.plantilla_logistica and self.producto_generico_ids:
            table_html += "<tr class='bg-primary'><td>Producto</td>"
            table_html += "<td>no SAP</td>"
            table_html += "<td>Categoria</td>"
            table_html += "<td>Descripcion</td>"
            table_html += "<td>Cantds a Solicitar</td>"
            table_html += "<td>Fecha Recibido</td>"
            table_html += "<td>Conformidad</td>"
            table_html += "<td>Firma</td></tr>"
            for product in self.producto_generico_ids:
                table_html += "<tr><td> %s </td>" % product.name
                table_html += "<td> %s </td>" % product.no_sap
                table_html += "<td> %s </td>" % product.categoria
                table_html += "<td> %s </td>" % product.descripcion
                table_html += "<td> %s </td>" % product.cantds_solicitar
                table_html += "<td>"  "</td>"
                table_html += "<td>"  "</td>"
                table_html += "<td>"  "</td></tr>"
        table_html += "</table>"
        self.vista_previa = table_html