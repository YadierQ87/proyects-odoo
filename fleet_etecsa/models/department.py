# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

#registro de licencias de circulacion de vehiculos
class fleet_etecsa_hr_department(models.Model):
    _name = "hr.department"
    _inherit = "hr.department"

    centro_costo_mlc = fields.Char("Centro Costo MLC")
    centro_costo_mn = fields.Char("Centro Costo MN")

