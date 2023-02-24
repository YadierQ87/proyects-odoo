# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from datetime import datetime
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class TallaVestuario(models.Model):
    _name = "demanda.talla.vestuario"
    _description = 'Talla Vestuario de Logistica'  # agregado

    name = fields.Char("Talla", required=True)
    metrica = fields.Selection([("europea", "europea"), ("americana", "americana"),("otra","otra")],string="Metrica:") # de la tabla de conversiones
    correspondencia = fields.Char("Corresponde a:")#Talla correspondiente a la metrica
    norma_talla_id = fields.Many2one("demanda.listado.tallas.vestuario")


#estas clases son para guardar los registros en el anexo de solicitud
class ListadoTallasVestuario(models.Model):
    _name = "demanda.listado.tallas.vestuario"
    _description = 'Listado de Tallas Vestuario de Logistica'  # agregado

    name = fields.Char("Grupo de Tallas", required=True)
    tallas_ids = fields.One2many("demanda.talla.vestuario",'norma_talla_id')


#esta clase es mas especifica
class ProductoVestuario(models.Model):
    _name = "demanda.producto.vestuario.logistica"
    _description = 'Producto Vestuario de Logistica'  # agregado

    name = fields.Char("Nombre Generico del Producto",required=True)
    talla_nacional = fields.Many2one("demanda.talla.vestuario",domain="[('norma_talla_id', '=',norma_talla)]")
    talla_extranjera = fields.Many2one("demanda.talla.vestuario",domain="[('norma_talla_id', '=',norma_talla)]")
    talla_especial = fields.Char("Talla Especial en cm")
    lleva_talla_especial = fields.Boolean("Lleva Talla Especial?")
    norma_talla = fields.Many2one('demanda.listado.tallas.vestuario',readonly=True)#viene de la plantilla
    descripcion = fields.Char("Descripción del Producto")
    categoria_talla = fields.Selection([("vestuario","vestuario"),("especial","especial")],readonly=True)
    solicitud_id = fields.Many2one("demanda.solicitud.vestuario",ondelete='cascade')  # Asociado a solicitud
    tipo_modulo_solicitud = fields.Char(related="solicitud_id.tipo_modulo",store=True)
    sexo_ropa = fields.Char(related="solicitud_id.sexo_modulo",store=True)
    html_tallas = fields.Html(compute="_cantidades_producto_x_talla")
    #para el cambio de vestuario , se oculta la talla_nacional y la talla_extranjera
    necesito_cambio = fields.Boolean("Necesito Cambio?", default=False)
    tengo_talla = fields.Many2one("demanda.talla.vestuario",domain="[('norma_talla_id', '=',norma_talla)]")
    necesito_talla = fields.Many2one("demanda.talla.vestuario",domain="[('norma_talla_id', '=',norma_talla)]")


    @api.model
    def _cantidades_producto_x_talla(self):
        lista_tallas = self.norma_talla.tallas_ids
        html_table = "<table><tr><td>productos</td>"
        for talla in lista_tallas:
            html_table += "<td>" + str(talla.name) + "</td>"
        html_table += "</tr>"
        self.html_tallas = html_table

    @api.model
    def listado_tallas_x_producto(self):
        if self.norma_talla:
            return self.norma_talla.tallas_ids


class SolicitudVestuario(models.Model):
    _name = "demanda.solicitud.vestuario" #cambiado uniforme
    _description = 'Planilla de Captación Vestuario'  # agregado
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(compute='_compute_solicitud_name', readonly=True)
    trabajador_id = fields.Many2one("hr.employee", string="Nombre trabajador",required=True)
    sexo_worker = fields.Char(compute='_compute_get_worker', string="Sexo")  # "trabajador_id.gender.name"
    depto_worker = fields.Char(compute='_compute_get_worker',string="Departamento")  # "trabajador_id.department_id.name"
    jefe_worker = fields.Char(compute='_compute_get_worker',string="Jefe Depto.")  # "trabajador_id.department_id.manager_id.name"
    active = fields.Boolean("Active?", default=True, track_visibility="always")
    plantilla_logistica = fields.Many2one("demanda.plantilla.logistica")  #Tipo de Plantilla
    tipo_modulo = fields.Char(related="plantilla_logistica.tipo_modulo")  # para el caso vestuario es Mod 1 o Mod 2
    sexo_modulo = fields.Char(related="plantilla_logistica.atributo_modulo")
    producto_vestuario_ids = fields.One2many("demanda.producto.vestuario.logistica",
                                             "solicitud_id")  # Lista de Tuplas Producto Vestuarios
    automatic_fields = fields.Html(compute="_action_automatic_assign", store=False)
    validacion = fields.Boolean(string="Llenar Planilla", default=True)
    vista_previa = fields.Html(compute="_get_plantilla_html", store=False)
    depto_solicitud_id = fields.Many2one("demanda.solicitud.vestuario.departamento",required=True)#todo required = true
    state = fields.Selection([("abierta","abierta"),("aprobada","aprobada"),("despachada","despachada"),("cerrada","cerrada")],track_visibility="always")
    nivel_satisfaccion = fields.Selection([("bueno","bueno"),("regular","regular"),("malo","malo")])#cuando se encuentre despachada
    #para tallas especiales
    lleva_talla_especial = fields.Boolean("Necesita talla especial?",default=False)
    cuello_cm = fields.Float("Medida del Cuello en cm")
    busto_pecho_cm = fields.Float("Medida del busto o pecho en cm")
    cintura_cm = fields.Float("Medida cintura en cm")
    cadera_cm = fields.Float("Medida de cadera en cm")
    ancho_brazo_cm = fields.Float("Ancho de brazo en cm")
    ancho_espalda_cm = fields.Float("Ancho de espalda en cm")
    largo_pierna_cm = fields.Float("Largo Total de pierna en cm")
    largo_torso_cm = fields.Float("Largo Total de torso en cm")


    @api.one
    @api.depends('trabajador_id', 'plantilla_logistica')
    def _compute_solicitud_name(self):
        today = datetime.today().strftime("%d/%m/%Y")
        if self.trabajador_id and self.plantilla_logistica:
            self.name = '%s del %s fecha %s' % (self.plantilla_logistica.name, self.trabajador_id.name, today)

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
    @api.depends('plantilla_logistica', 'validacion')  # Llenar los valores de la tupla
    def action_automatic_assign(self):
        if self.plantilla_logistica:
            ProductoVestuario = self.env['demanda.producto.vestuario.logistica']
            if self.producto_vestuario_ids:
                lista_nombre_logistica = self.plantilla_logistica.producto_ids.mapped("name")
                for product_in in self.producto_vestuario_ids:
                    if lista_nombre_logistica.count(product_in.name) == -1:
                        # se eliminan los valores que no estan a la plantilla
                        rec = ProductoVestuario.search([('id', '=', product_in.id)])
                        rec.unlink()
                lista_nombre_genericos = self.producto_vestuario_ids.mapped("name")
                for product_x in self.plantilla_logistica.producto_ids:
                    if lista_nombre_genericos.count(product_x.name) == -1:
                        # Insertar los nuevos que estan en la plantilla sin estar repetidos
                        ProductoVestuario.create({'name': product_x.name,
                                                  'categoria_talla': product_x.categoria,
                                                  'norma_talla': product_x.tipo_vestuario.id,
                                                  'solicitud_id': self.id})
            else:
                for product_x in self.plantilla_logistica.producto_ids:
                    ProductoVestuario.create({'name': product_x.name,
                                              'categoria_talla': product_x.categoria,
                                              'norma_talla': product_x.tipo_vestuario.id,
                                              'solicitud_id': self.id})
        if self.validacion:
            self.validacion = False

    @api.one
    @api.depends('plantilla_logistica', 'producto_vestuario_ids')
    def _get_plantilla_html(self):
        table_html = "<table class='table table-bordered table-hover'>"
        if self.plantilla_logistica and self.producto_vestuario_ids:
            table_html += "<tr><td>Producto</td>"
            table_html += "<td>Talla Nacional</td>"
            table_html += "<td>Talla Extranjera</td>"
            table_html += "<td> Talla Especial </td>"
            for attr in self.plantilla_logistica.attrs_ids:  # pintar todos los atributos
                table_html += "<td>" + attr.name + "</td>"
            table_html += "</tr>"
            for product in self.producto_vestuario_ids:
                table_html += "<tr><td> %s </td>" % product.name
                table_html += "<td> %s </td>" % product.talla_nacional.name
                table_html += "<td> %s </td>" % product.talla_extranjera.name
                if product.lleva_talla_especial:
                    table_html += "<td> %s </td>" % product.talla_especial
                else:
                    table_html += "<td> --not set-- </td>"
                for attr in self.plantilla_logistica.attrs_ids:
                    table_html += "<td><input type='text' placeholder='value'/></td>"
                table_html += "</tr>"
        table_html += "</table>"
        self.vista_previa = table_html

# Solo se abre una por año y por departamento
class SolicitudVestuarioDepartamento(models.Model):
    _name = "demanda.solicitud.vestuario.departamento"
    _description = 'Demanda de Vestuario x Depto'  # agregado
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string='Numero de la Solicitud',store=True,readonly=True,default='New')
    departamento_id = fields.Many2one("hr.department", required=True)
    jefe_depto = fields.Many2one(related="departamento_id.manager_id")
    active = fields.Boolean(default=True)
    solicitudes_ids = fields.One2many("demanda.solicitud.vestuario",'depto_solicitud_id')
    demanda_division_id = fields.Many2one("demanda.solicitud.vestuario.division")
    observaciones = fields.Text()
    totales = fields.Html(compute="do_create_table_total") #todo recorrer todas las solicitudes y devolver una lista total y un reporte

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sequence.demanda.vestuario.depto') or 'New'
        result = super(SolicitudVestuarioDepartamento, self).create(vals)
        return result

    # -- para modelar todas las cantidades de ropa x talla en los modelos guardados --#
    @api.multi
    def do_create_table_total(self):
        #listado de las solicitudes del dpto
        ProductoVestuario = self.env['demanda.producto.vestuario.logistica']
        SolicitudVestuario = self.env['demanda.solicitud.vestuario']
        TallaVestuario = self.env["demanda.talla.vestuario"]

        solicitudes_ids = SolicitudVestuario.search([('depto_solicitud_id','=',self.id)]).mapped('id')
        #_logger.info('Las solicitudes %s', solicitudes_ids)
        #listado de productos en esas solicitudes
        html = "<p>No existen solicitudes aun</p>"
        if solicitudes_ids:
            productos_ids = ProductoVestuario.search([('solicitud_id','in',solicitudes_ids)]).mapped('id')
            str1 = ','.join(str(e) for e in solicitudes_ids)
            self.env.cr.execute(f'SELECT distinct sexo_ropa,tipo_modulo_solicitud,name,norma_talla FROM demanda_producto_vestuario_logistica WHERE  solicitud_id in ({str1}) order by tipo_modulo_solicitud,sexo_ropa')
            listado = self.env.cr.dictfetchall()
            html = "<table class='table table-bordered table-striped'><tr><td>Producto</td></tr>"
            if listado:
                modulo = ""
                for product in listado:
                    total_vestuarios = 0
                    if modulo != f'Modulo {product["tipo_modulo_solicitud"]} {product["sexo_ropa"]}':
                        modulo = f'Modulo {product["tipo_modulo_solicitud"]} {product["sexo_ropa"]}'
                        html += "<tr><th> Total de piezas  x Tallas %s </th></tr>" % modulo
                    html += "<tr><td>  %s </td>" % product["name"]
                    tallas_list = TallaVestuario.search([('norma_talla_id', '=', product["norma_talla"])])
                    for talla in tallas_list:
                        html += "<td>" + talla.name + " </td>"

                    html += "<td>Total</td></tr><tr><td>-</td>"
                    for talla in tallas_list:
                        cantd_vestuarios = ProductoVestuario.search_count([('talla_nacional','=',talla.name),('id','in',productos_ids),('name','=',product["name"])])
                        total_vestuarios += cantd_vestuarios
                        html += "<td>" + str(cantd_vestuarios)  + " </td>"
                    html += "<td>" + str(total_vestuarios) +"</td></tr>"
            html += "</table>"
        self.totales = html


#Clase Total para solicitar vestuarios por division territorial
#Solo se abre una por año y el unico usuario es el admin del grupo.
class SolicitudVestuarioDivision(models.Model):
    _name = "demanda.solicitud.vestuario.division"
    _description = 'Demanda Global de Vestuario x Division'  # agregado
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string='Numero de la Solicitud',store=True,readonly=True,default='New')
    nombre_division = fields.Char()
    periodo_solicitado = fields.Char()
    fecha_inicio = fields.Date()
    fecha_cierre = fields.Date()
    director_encargado = fields.Many2one("res.partner")
    doc_aprobado = fields.Binary()
    observaciones = fields.Html()
    active = fields.Boolean(default=True)
    departamento_ids = fields.One2many("demanda.solicitud.vestuario.departamento","demanda_division_id")
    totales = fields.Html(compute="do_create_table_total")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sequence.demanda.vestuario.division') or 'New'
        result = super(SolicitudVestuarioDivision, self).create(vals)
        return result

    # -- para modelar todas las cantidades de ropa x talla en los modelos guardados --#
    @api.multi
    def do_create_table_total(self):
        # listado de las solicitudes del dpto
        ProductoVestuario = self.env['demanda.producto.vestuario.logistica']
        SolicitudVestuario = self.env['demanda.solicitud.vestuario']
        TallaVestuario = self.env["demanda.talla.vestuario"]
        Departamentos = self.env["demanda.solicitud.vestuario.departamento"]

        departamento_ids = Departamentos.search([('demanda_division_id', '=', self.id)]).mapped('id')
        solicitudes_ids = SolicitudVestuario.search([('depto_solicitud_id', 'in', departamento_ids)]).mapped('id')
        # _logger.info('Las solicitudes %s', solicitudes_ids)
        html = "<p>No existen solicitudes aun</p>"
        if solicitudes_ids:
            productos_ids = ProductoVestuario.search([('solicitud_id', 'in', solicitudes_ids)]).mapped('id')
            str1 = ','.join(str(e) for e in solicitudes_ids)
            self.env.cr.execute(
                f'SELECT distinct sexo_ropa,tipo_modulo_solicitud,name,norma_talla FROM demanda_producto_vestuario_logistica WHERE  solicitud_id in ({str1}) order by tipo_modulo_solicitud,sexo_ropa')
            listado = self.env.cr.dictfetchall()
            html = "<table class='table table-bordered table-striped'><tr><td>Producto</td></tr>"
            if listado:
                modulo = ""
                for product in listado:
                    total_vestuarios = 0
                    if modulo != f'Modulo {product["tipo_modulo_solicitud"]} {product["sexo_ropa"]}':
                        modulo = f'Modulo {product["tipo_modulo_solicitud"]} {product["sexo_ropa"]}'
                        html += "<tr><th> Total de piezas  x Tallas %s </th></tr>" % modulo
                    html += "<tr><td>  %s </td>" % product["name"]
                    tallas_list = TallaVestuario.search([('norma_talla_id', '=', product["norma_talla"])])
                    for talla in tallas_list:
                        html += "<td>" + talla.name + " </td>"

                    html += "<td>Total</td></tr><tr><td>-</td>"
                    for talla in tallas_list:
                        cantd_vestuarios = ProductoVestuario.search_count(
                            [('talla_nacional', '=', talla.name), ('id', 'in', productos_ids),
                             ('name', '=', product["name"])])
                        total_vestuarios += cantd_vestuarios
                        html += "<td>" + str(cantd_vestuarios) + " </td>"
                    html += "<td>" + str(total_vestuarios) + "</td></tr>"
            html += "</table>"
        self.totales = html