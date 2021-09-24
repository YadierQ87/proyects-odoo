# coding: utf-8
from odoo import api,fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    linkedin_account = fields.Char( string="Linkedin Account",
                                    help="Your account at Linkedin")
    facebook_account = fields.Char( string="Facebook Account",
                                    help="Your account at Facebook")
    twitter_account = fields.Char( string="Twitter Account",
                                   help="Your account at Twitter")
    profile_status = fields.Boolean(string="Estado del perfil",)
    status_html = fields.Html(compute='compute_profile_status',
                              default="<span>Profile Incomplete</span>",
                              string="Social Media")

    @api.depends('linkedin_account','facebook_account','twitter_account')
    def compute_profile_status(self):
        for record in self:
            record.profile_status = False
            record.status_html = "<span>Profile Incomplete</span>"
            if record.linkedin_account and record.facebook_account and record.twitter_account:
                record.profile_status = True
                record.status_html = "<img src='%s' style='width:70px' /> <span>Profile Completed!</span>" % "/crm_social_profile/static/src/img/confirm.png"