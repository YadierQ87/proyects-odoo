# -*- coding: utf-8 -*-
from odoo import models, fields, api,tools

class ProductoPlantillaLogistica(models.Model):
    _name = "demanda.producto.plantilla.logistica"
    _description = 'Producto Generico de Plantilla Logistica'  # agregado

    name = fields.Char("Nombre Genérico del Producto")
    categoria = fields.Selection([("inmueble", "inmueble"), ("insumo", "insumo"), ("herramienta", "herramienta"),
                                  ("otros", "otros"),("vestuario", "vestuario"),("especial", "especial")])
    tipo_vestuario = fields.Many2one('demanda.listado.tallas.vestuario',string="Tipo de Talla")
    plantilla_id = fields.Many2one("demanda.plantilla.logistica")

class AtributoPlantillaLogistica(models.Model):
    _name = "demanda.atributo.plantilla.logistica"
    _description = 'Atributos de Plantilla Logistica'  # agregado

    name = fields.Char("Atributo Logistica")
    plantilla_id = fields.Many2one("demanda.plantilla.logistica")

class PlantillaLogistica(models.Model):
    _name = "demanda.plantilla.logistica"
    _description = 'Plantilla Logistica para las demandas'  # agregado
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Nombre del Anexo")#nombre del Anexo
    active = fields.Boolean("Active?", default=True, track_visibility="always")
    categoria_id = fields.Many2one("product.category", string="Categoria de la Plantilla")
    tipo_modulo = fields.Char()#para el caso vestuario es Mod 1 o Mod 2
    atributo_modulo = fields.Char()#para el caso vestuario es Masculino o Femenino
    producto_ids = fields.One2many('demanda.producto.plantilla.logistica', 'plantilla_id',string="Selección de Productos y Cantidades")#listado de productos
    attrs_ids = fields.One2many('demanda.atributo.plantilla.logistica', 'plantilla_id',string="Atributos de la plantilla")#listado de elementos asociados
    vista_previa = fields.Html(compute="_get_plantilla_html",store=False)
    encabezado = fields.Html(store=True)
    pie_pagina = fields.Html(store=True)

    @api.one
    @api.depends('attrs_ids','producto_ids')
    def _get_plantilla_html(self):
        self.vista_previa = ""
        table_html = "<table class='table table-bordered table-hover'>"
        if self.attrs_ids and self.producto_ids:
            table_html += "<tr class='bg-primary'><td>Producto</td>"
            for attr in self.attrs_ids:#pintar todos los atributos
                if attr.name:
                    table_html += "<td> %s  </td>" % attr.name
            table_html += "</tr>"
            for product in self.producto_ids:
                if product.name:
                    table_html += "<tr><td> %s </td>" % product.name
                for attr in self.attrs_ids:
                        table_html += "<td><input type='text' placeholder='value'/></td>"
                table_html += "</tr>"
        table_html += "</table>"
        if self.encabezado:
            self.vista_previa += self.encabezado
        if table_html:
            self.vista_previa += table_html
        if self.pie_pagina:
            self.vista_previa += self.pie_pagina

    #TODO campo computado va generando la plantilla en html como vista previa


