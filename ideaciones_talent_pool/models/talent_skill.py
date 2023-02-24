from odoo import fields, models, api


# specialty nomenclatures
class ResPartnerSpecialty(models.Model):
    _name = 'res.partner.specialty'
    _description = 'Professional specialities'

    name = fields.Char(string="Specialty name")


# skills nomenclatures
class ResPartnerSkill(models.Model):
    _name = 'res.partner.skill'
    _description = 'Professional Skills'

    name = fields.Char(string="Skill")


# lines of competences for res.partner
class LinesCompetences(models.Model):
    _name = 'res.partner.competences'
    _description = 'Lines of Competences'

    """One partner type=colaborator could have many lines of competences"""
    specialty = fields.Many2one(
        comodel_name='res.partner.specialty',
        string='Specialty',
        required=False)
    skills_ids = fields.Many2many(
        comodel_name='res.partner.skill',
        string='Skills')
    partner_id = fields.Many2one("res.partner")
    user_ids = fields.One2many(
        comodel_name="res.users",
        related="partner_id.user_ids"
    )


# main acknowledgments obtained
class LinesAcknowledgments(models.Model):
    _name = 'res.partner.acknowledgments'
    _description = 'Acknowledgments'

    name = fields.Char()
    description = fields.Text()
    partner_id = fields.Many2one("res.partner")
    user_ids = fields.One2many(
        comodel_name="res.users",
        related="partner_id.user_ids"
    )
