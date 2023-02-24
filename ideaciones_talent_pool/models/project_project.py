from odoo import fields, models, api


class Projectproject(models.Model):
    _inherit = 'project.project'

    team_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Colaborator in Team')
