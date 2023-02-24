# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import date,datetime
from dateutil.relativedelta import relativedelta

#todo cambiar por res.partner
class SerclinicContacts(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'
    _order = 'id desc'

    hospital_contact_type = fields.Selection([
        ("Hospital","Hospital"),
        ("Paciente","Paciente"),
        ("Doctor","Doctor")
    ],string='Tipo de Contacto',default="Paciente")
    country_id = fields.Many2one('res.country', string='País', default=51)
    province_id = fields.Many2one('res.country.state', string='Provincia', context="[('country_id.id', '=','51')]")
    municipality_id = fields.Many2one('serclinic.municipality', string='Municipio',
                                      context="[('province_id', '=',province_id)]")
    # #Solo para para pacientes y workers
    @api.depends('date_of_birth')
    def onchange_age(self):
        for line in self:
            if line.date_of_birth:
                d1 = line.date_of_birth
                d2 = datetime.today().date()
                rd = relativedelta(d2, d1)
                line.age = str(rd.years) + " años " + " " + str(rd.months) + " meses" + " " + str(rd.days) + " días"
            else:
                line.age = "No tiene fecha de Nacimiento aún!!"

    @api.depends('date_of_birth')
    def onchange_age_integer(self):
        for line in self:
            if line.date_of_birth:
                d1 = line.date_of_birth
                d2 = datetime.today().date()
                rd = relativedelta(d2, d1)
                line.edad_int = rd.years

    data_ci = fields.Char('CI', size=11, required=True)
    sex = fields.Selection([('m', 'Masculino'), ('f', 'Femenino')], string="Sexo")
    date_of_birth = fields.Date(string="Fecha de Nacimiento", required=True, default=fields.Date.today())
    code = fields.Char('No Expediente Paciente', copy=False, default='New',readonly=True)#autogenerado sequence
    mobile_number = fields.Char(string="Móvil")
    age = fields.Char(compute=onchange_age, string="Edad", store=True)
    age_int = fields.Integer(compute=onchange_age_integer, string="Años (int)", store=False)

    def print_report(self):
        self.ensure_one()
        self.sent = True
        return self.env.ref('hospital_management.report_print_patient_card').report_action(self)

    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New' and vals.get('hospital_contact_type') == "Paciente":#solo para los pacientes
            vals['code'] = self.env['ir.sequence'].next_by_code(
                'serclinic.paciente') or 'New'
        result = super(SerclinicContacts, self).create(vals)
        return result

    def _compute_count_all(self):
        Turno = self.env['serclinic.turno.medico.paciente']
        for record in self:
            record.turn_medicos_count = Turno.search_count([('patient_id', '=', record.id)])

    def return_action_to_open(self):
        """ This opens the xml view estudio medico specified in xml_id for the current patient """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window'].for_xml_id('serclinic', xml_id)
            res.update(
                context=dict(self.env.context, default_patient_id=self.id, group_by=False),
                domain=[('patient_id', '=', self.id)]
            )
            return res
        return False





#Trabajadores del Hospital
#TODO cambiar por hr.employee
class SerclinicWorkersClinic(models.Model):
    _name = 'hr.employee'
    _inherit = "hr.employee"
    _order = 'id desc'

    hospital_worker = fields.Selection([
        ("Especialista", "Especialista"),
        ("Tecnico", "Tecnico"),
        ("Trabajador", "Trabajador"),
        ("Otro", "Otro")
    ], string='Tipo de Trabajador')
    coname = fields.Selection([("doctor","Dr."),("master","Msc."),
                               ("ingeniero","Ing."),
                               ("licenciado","Lic."),
                               ("sir","Sr."),
                               ("sira","Sra."),
                               ("specialist","Esp."),
                               ("tecnico","Tec."),
                               ("worker","Trab.")]
                              ,string="Presentacion")
    relevant_info = fields.Text(string="Datos Clínicos Relevantes")
    occupation_in_hospital = fields.Char(string="Cargo Hospital")


