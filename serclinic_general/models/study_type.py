# coding=utf-8
from odoo import models, fields, api,tools, _
from datetime import datetime,timedelta

#Tipo de Estudio Medico
def _get_nombre_day(dia_semana):
    if dia_semana == 0:
        return "Lunes"
    if dia_semana == 1:
        return "Martes"
    if dia_semana == 2:
        return "Miercoles"
    if dia_semana == 3:
        return "Jueves"
    if dia_semana == 4:
        return "Viernes"
    if dia_semana == 5:
        return "Sabado"
    if dia_semana == 6:
        return "Domingo"


class SerclinicMedicalStudyType(models.Model):
    _name = 'serclinic.medical.study.type'
    _description = 'Tipo Estudio Médico'

    name = fields.Char(string='Nombre del Estudio',required=True)
    description = fields.Text(string='Descripción del Estudio',required=True)
    active = fields.Boolean('Activo?', default=True, track_visibility='always')
    price = fields.Float('Precio del Estudio')
    money = fields.Many2one('res.currency',string='Moneda')
    is_dinamic = fields.Boolean('Es Dinamico?', default=False)
    observations = fields.Text('Observaciones')
    dosis_suggest = fields.Float('Dosis Sugerida')
    # table_for_15days = fields.Html(compute="_get_dates_availables_by_type",
    #                                   string='Tabla de Turnos Próximos 15 días',store=False) TODO in estudios
    #relaciones con otras tablas    #One2many es una lista
    zones_administracion_ids = fields.Many2many('serclinic.cod.adm.zones',
                                                string='Zonas de Administracion')
    # nombre_radiofarmacos_id = fields.Many2many('serclinic.cod.nombre.radiofarmacos',
    #                                            string='Radiofarmacos Asociados') TODO heredar en radiofarmacos
    steps_study_medical_id = fields.Many2many('serclinic.medical.study.steps',
                                               string='Pasos del Estudio Medico')
    plan_week_id = fields.One2many('serclinic.plan.week',
                                               'tipo_estudio_id',
                                               string='Planificacion Semanal',required=False)#TODO en turno relation calendar

#Codificador Zonas de Administracion
class SerclinicCodAdministrationZones(models.Model):
    _name = 'serclinic.cod.adm.zones'
    _description = 'Zonas de Administracion del Estudio'

    name = fields.Char('Zona de Administracion')


#Codificador Pasos del Estudio Medico
class SerclinicMedicalStudySteps(models.Model):
    _name = 'serclinic.medical.study.steps'
    _description = 'Pasos del Estudio Medico'

    name = fields.Char('Paso del Estudio Medico')


#Codificador Planificacion Semanal
class SerclinicPlanWeek(models.Model):
    _name = 'serclinic.plan.week'
    _description = 'Planificacion Semanal del Estudio'
    _order = "week_day asc"

    #name = fields.Char('planificacion')
    # Funcion weekday 0-Lunes, 1-Martes, 2-Miércoles, 3-Jueves, 4-Viernes , 5-Sábado y 6-Domingo
    week_day = fields.Selection([("6","Domingo"),("0","Lunes"),
                                   ("1","Martes"),("2","Miercoles"),
                                   ("3","Jueves"),("4","Viernes"),
                                   ("5","Sabado")],required=True)
    qty_days = fields.Integer('Cantidad de dias',required=True)
    tipo_estudio_id = fields.Many2one('serclinic.study.type',
                                      string="Tipo de Estudio Médico",ondelete='cascade',readonly=True )

    #constraint week_day,qty_days,tipo_estudio_id UNIQUE
    _sql_constraints = [
        ('planificacion_dias_estudio_unique', 'UNIQUE (tipo_estudio_id, week_day)',
                        'Revise la planificación,No puede haber dias repetidos!')]




