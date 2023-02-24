# -*- coding: utf-8 -*-

from datetime import date, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"
    """To registers the clients"""

    name = fields.Char(string="Name", required=True)
    last_name = fields.Char(string="Last name")
    age = fields.Integer(string="Age", store=True)
    date_birth = fields.Date(string="Date of Birth")
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
        ],
        string="Gender",
    )
    is_customer = fields.Boolean(
        string='Is Customer',
        required=False)

    @api.onchange("date_birth")
    def calculated_age(self):
        today = date.today()
        if self.date_birth:
            self.age = today.year - self.date_birth.year

    def return_action_view_records(self):
        """This opens the xml view with context"""
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "agendmedic.medical_record_act_window"
        )
        action["context"] = {
            "default_patients_id": self.id,
            "default_medical_record_ids": self.medical_record_ids,
        }
        return action
