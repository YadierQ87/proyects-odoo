from odoo import api,models, fields
from odoo.exceptions import ValidationError


class LineInvoiceLead(models.Model):
    _name = 'line.invoice.crm.lead'
    _description = 'Line Invoice for Lead'

    name = fields.Char("Description")
    cost_value = fields.Float("Cost value")
    crm_lead_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Opportunity',
        required=False)


class TeamMember(models.Model):
    _name = 'crm.team.member'
    _description = "The member for a team in crm"

    hr_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Colaborator',
        required=False)
    points = fields.Float(
        string='Points',
        required=False)


class CrmLeads(models.Model):
    _name = 'crm.lead'
    _inherit = 'crm.lead'

    # new fields for info
    title_contact = fields.Char("Título")
    lastname = fields.Char("Apellidos")
    company_name = fields.Char("Nombre Empresa")
    job_title = fields.Selection(
        string='Presentación',
        selection=[
            ('Decisor político', 'Decisor político'),
            ('Administrativo', 'Administrativo'),
            ('Académico', 'Académico'),
            ('Otro', 'Otro'),
        ]
    )
    interested = fields.Char("Interés principal")
    observation = fields.Text(
        string="Observations",
        required=False)
    preferences = fields.Char("Medios de comunicación preferido")
    type_contact = fields.Selection(
        string='Tipo de Empresa',
        selection=[
            ('Organismo multilateral', 'Organismo multilateral'),
            ('Gobierno', 'Gobierno'),
            ('ONG', 'ONG'),
            ('Universidad', 'Universidad'),
            ('Instituciones educativas', 'Instituciones educativas'),
            ('Otras Instituciones', 'Otras Instituciones'),
        ],
        required=False, )
    country_id = fields.Many2one('res.country')
    # who defines this skills , the client or the user?
    partner_skill_ids = fields.Many2many(
        comodel_name='res.partner.skill',
        string='Skills needed')  # competencias necesarias
    specialty_ids = fields.Many2many(
        comodel_name='res.partner.specialty',
        string='Specialty needed')  # areas del conocimiento o especialidades
    team_members_ids = fields.Many2many(
        comodel_name='crm.team.member',
        string='Team members')
    is_project = fields.Boolean(
        string='Is project',
        required=False)
    project_type = fields.Char("Project Type")
    pre_invoice_line_ids = fields.One2many(
        comodel_name='line.invoice.crm.lead',
        inverse_name='crm_lead_id',
        string='Lines of pre-invoice',
        required=False)
    cost_invoice = fields.Float(
        compute="_get_cost_pre_invoice",
        string="Cost Invoice",
        default=0.0
    )

    @api.depends('pre_invoice_line_ids')
    def _get_cost_pre_invoice(self):
        cost_invoice = 0
        if self.pre_invoice_line_ids:
            for line in self.pre_invoice_line_ids:
                cost_invoice += line.cost_value
        self.cost_invoice = cost_invoice

    """ Tener en cuenta las variables o criterios de medida para conformar el Team?"""
    # generar    # por lineas de experiencia    # por competencias

    def suggest_talent(self):
        """ suggest the talent employee that have the needed skills """
        if self.partner_skill_ids:
            all_colaborator = self.env["res.partner"].search([('type_partner', '=', 'colaborador')])
            # only colaboradores in the talent pool
            talent_bag = []
            for colaborator in all_colaborator:
                counter = 0
                for skill in self.partner_skill_ids:
                    for competence in colaborator.competences_ids:
                        for sk in competence.skills_ids:
                            if skill.id == sk.id:
                                counter += 1
                if counter > 0:  # what its the percent of fulfillment
                    talent_bag.append(
                        {
                            "hr_partner_id": colaborator.id,
                            "points": counter
                        }
                    )
            talent_bag = sorted(talent_bag, key=lambda d: d['points'])
            CrmTeamMember = self.env["crm.team.member"]
            # the minimum or maximum number for team member
            for talent in talent_bag:
                new_member = CrmTeamMember.create(talent)
                self.team_members_ids |= new_member
        else:
            raise ValidationError('Para sugerir candidatos debe seleccionar al menos una competencia')

    def create_project_from_lead(self):
        """ create a project from the leads """
        ProjectProject = self.env["project.project"]
        new_project = ProjectProject.create(
            {
                "name": self.name,
                "description": self.description,
            }
        )
        if self.team_members_ids:
            for member in self.team_members_ids:
                new_project.team_partner_ids |= member.hr_partner_id
        self.is_project = True
