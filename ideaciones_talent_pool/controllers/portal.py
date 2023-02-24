# -*- coding: utf-8 -*-
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, get_records_pager


class CustomerPortal(CustomerPortal):

    """For passing values and vars to the main page for user Home"""
    def _prepare_portal_layout_values(self):

        sales_user = False
        countries = request.env["res.country"].sudo().search([])
        titles = request.env["res.partner.title"].sudo().search([])
        contacts = request.env["res.preference.contact"].sudo().search([])
        partner = request.env.user.partner_id
        project_count = request.env['project.project'].search_count([])  # todo domain for user
        task_count = request.env['project.task'].search_count([])
        welcome = partner.welcome
        if partner.user_id and not partner.user_id._is_public():
            sales_user = partner.user_id
        return {
            'sales_user': sales_user,
            'titles': titles,
            'countries': countries,
            'project_count': project_count,
            'task_count': task_count,
            'contacts': contacts,
            'sms_welcome': welcome,
            'page_name': 'home',
        }



