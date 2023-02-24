from odoo import fields, models


# Experience category nomenclatures
class CurriculumTypesLines(models.Model):
    _name = 'cv.experience.category'
    _description = 'Experience category'

    name = fields.Char(string="Experience category")


# main experiences obtained for partner
class ExperiencesLines(models.Model):
    _name = 'res.partner.experience.line'
    _description = 'Experiences for partner'

    name = fields.Char(string="Name or Title")
    period = fields.Char(string="Date-Period or Year")  # (date_begin - date_end)
    role_function = fields.Char(string="Role or function")
    institution = fields.Char(string="Organization or Institution")
    type = fields.Char(string="Type")
    specialty_id = fields.Many2one("res.partner.specialty")
    category_id = fields.Many2one("cv.experience.category")
    duration = fields.Char(string="Duration")
    country_id = fields.Many2one("res.country")
    description = fields.Text(string="Details or description")
    observations = fields.Text(string="Observations")
    notes = fields.Text(string="Notes")
    url_website = fields.Char(
        string='URL / DOI',
        required=False)
    qty_credits = fields.Integer(
        string='Credits',
        required=False)
    editorial = fields.Char(
        string='Editorial',
        required=False)
    partner_id = fields.Many2one("res.partner")
    user_ids = fields.One2many(
        comodel_name="res.users",
        related="partner_id.user_ids"
    )
