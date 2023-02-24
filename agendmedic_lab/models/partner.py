# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    order_lab_ids = fields.One2many(
        comodel_name='order.exams.lab',
        inverse_name='patient_id',
        string='Ordenes de Laboratorio',
        required=False)
    order_count = fields.Integer(compute="get_count_order_lab_ids")
    t_sex = fields.Selection(
        string='Sexo',
        selection=[('M', 'Masculino'),
                   ('F', 'Femenino'), ],
        required=False, )
    t_birthday = fields.Date(
        string='Fecha de Nacimiento',
        required=False)
    t_age = fields.Char(string="Edad", compute="compute_age")

    @api.depends('t_birthday')
    def compute_age(self):
        for rec in self:
            if rec.t_birthday:
                d1 = rec.t_birthday
                d2 = datetime.today().date()
                rd = relativedelta(d2, d1)
                if rd.years <= 2:
                    rec.t_age = str(rd.years) + "año(s)" + " " + str(rd.months) + "meses" + " " + str(rd.days) + "días"
                else:
                    rec.t_age = str(rd.years) + "año(s)"
            else:
                rec.t_age = "Sin fecha de Nacimiento!!"

    @api.depends('order_lab_ids')
    def get_count_order_lab_ids(self):
        for item in self:
            if item.order_lab_ids:
                item.order_count = len(item.order_lab_ids)
            else:
                item.order_count = 0

    def return_action_view_orders(self):
        """This opens the xml view with context"""
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "agendmedic_lab.order_exams_for_partner_act_window"
        )
        action["context"] = {
            "default_patient_id": self.id,
            "default_order_lab_ids": self.order_lab_ids,
        }
        return action
