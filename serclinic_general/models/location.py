from odoo import models, fields, api,tools, _

#Provincia
class SerclinicProvince(models.Model):
    _name = 'res.country.state'
    _inherit = 'res.country.state'
    municipio_ids = fields.One2many('serclinic.municipality','province_id',domain="[(id,'=',province_id)]")

class SerclinicMunicipality(models.Model):
    _name = 'serclinic.municipality'
    _description = 'Municipios'
    name = fields.Char(string='Nombre del Municipio',required=True)
    province_id = fields.Many2one('res.country.state')