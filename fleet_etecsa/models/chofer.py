# -*- coding: utf-8 -*-

from odoo import models, fields, api

#nomenclador Categoria de Licencia
class fleet_etecsa_cat_licencia(models.Model):
    _name = "fleet.etecsa.cat.licencia"
    _description = "Categorias de Licencia"

    name = fields.Char()
    description = fields.Text()


#choferes se enlaza con Empleado
class fleet_etecsa_chofer(models.Model):
    _name = "fleet.etecsa.chofer"
    _description = "Choferes de ETECSA"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Numero de Licencia")
    employee_id = fields.Many2one("hr.employee", "Nombre del Trabajador", tracking=True)
    foto_licencia = fields.Binary()
    fecha_expedida_licencia = fields.Date()
    fecha_vencimiento_licencia = fields.Date()
    categoria_licencia = fields.Many2many("fleet.etecsa.cat.licencia")
    active = fields.Boolean("Active?", default=True, track_visibility="always")
