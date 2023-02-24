import re

from odoo import fields, models

from ..tools.field_validator import FieldValidator


class ResPartner(models.Model):
    _inherit = "res.partner"

    birthday = fields.Date("Fecha de nacimiento")
    title_contact = fields.Char("Titulo")
    work_email = fields.Char("Correo Institucional")
    lastname = fields.Char("Apellidos")
    job_title = fields.Selection(
        string="Tipo de Administrativo",
        selection=[
            ("Decisor político", "Decisor político"),
            ("Administrativo", "Administrativo"),
            ("Académico", "Académico"),
            ("Otros", "Otros"),
        ],
        required=False,
    )
    interested = fields.Char("Interés principal")
    passport = fields.Char("Pasaporte")
    province = fields.Char("Provincia")
    ci_number = fields.Char("CI")
    sex = fields.Selection(
        [
            ("femenino", "femenino"),
            ("masculino", "masculino"),
            ("other", "otro"),
        ]
    )
    whatsapp = fields.Char(string="whatsapp", required=False)
    facebook = fields.Char(string="facebook", required=False)
    orcid = fields.Char(string="orcid", required=False)
    linkedin = fields.Char(string="linkedin", required=False)
    website_own = fields.Char(string="Sitio web personal", required=False)
    summary_cv = fields.Text(string="Resumen del CV", required=False)
    observation = fields.Text(string="Observations", required=False)
    speciality = fields.Char(string="Titulo/Especialidad", required=False)
    status_work = fields.Char(string="Estado laboral actual", required=False)
    job_name = fields.Char(string="Puesto de trabajo actual", required=False)
    institution = fields.Char(string=" Institución a la que pertenece", required=False)
    ministery = fields.Char(string=" Ministerio al que pertenece", required=False)
    preferences = fields.Selection(
        string="Medios de comunicación preferido",
        selection=[
            ("Telefono", "Telefono"),
            ("Correo", "Correo"),
            ("Whatsapp", "Whatsapp"),
            ("Linkedin", "Linkedin"),
            ("Telegram", "Telegram"),
            ("Zoom", "Zoom"),
        ],
    )
    pref_contact_ids = fields.Many2many(
        "res.preference.contact",
        "res_partner_res_preference_contact_rel",
        "res_partner_id",
        "res_preference_contact_id",
        string="Medios de comunicación preferido",
    )
    new_pref_contacts = fields.Char()
    type_contact = fields.Selection(
        string="Representante de",
        selection=[
            ("Organismo multilateral", "Organismo multilateral"),
            ("Gobierno", "Gobierno"),
            ("ONG", "ONG"),
            ("Universidad", "Universidad"),
            ("Instituciones educativas", "Instituciones educativas"),
            ("Otras Instituciones", "Otras Instituciones"),
        ],
        required=False,
    )
    type_partner = fields.Selection(
        [
            ("cliente", "cliente"),
            ("colaborador", "colaborador"),
            ("internal", "internal"),
        ],
        string="Tipo de Contacto",
    )
    # list of competences
    competences_ids = fields.One2many(
        comodel_name="res.partner.competences",
        inverse_name="partner_id",
        string="Lines of competences",
        required=False,
    )
    # list of acknowledgments, badges, achievements
    acknowledge_ids = fields.One2many(
        comodel_name="res.partner.acknowledgments",
        inverse_name="partner_id",
        string="Lines of acknowledgments",
        required=False,
    )
    experience_ids = fields.One2many(
        comodel_name="res.partner.experience.line",
        inverse_name="partner_id",
        string="List of Experiences",
        required=False,
    )
    teaching_category = fields.Char(string="Categoría Docente")
    researcher_category = fields.Char(string="Categoría Investigador")
    welcome = fields.Integer(
        "First Login", default=0
    )  # only for showing welcome message


class PartnerValidator(FieldValidator):
    def validate_ci(self, term):
        if not re.fullmatch(r"([\d]{11})", term):
            return {"error": "CI incorrecto"}
        return {}

    def validate_orcid(self, term):
        if not re.fullmatch(r"(?:(?:http|https):\/\/)?orcid\.org\/([\w\.])+", term):
            return {"error": "URL de perfil orcid inválida"}
        return {}
