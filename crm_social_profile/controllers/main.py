# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import werkzeug
from odoo import http, fields , _
from odoo.addons.website.controllers.main import QueryURL
from odoo.http import request
from odoo.addons.portal.controllers.portal import pager as portal_pager
import logging
_logger = logging.getLogger(__name__)

class CrmSocialProfile(http.Controller):

    @http.route(['/crm/customers/','/crm/customers/<int:page>'], auth='public',website=True)
    def index(self, page=1,  search='', **kw):
        ResPartner = request.env["res.partner"]
        domain = request.website.website_domain()
        if search:
            domain += ['|','|','|',
                       ('name', 'ilike', search),
                       ('linkedin_account', 'ilike', search),
                       ('facebook_account', 'ilike', search),
                       ('twitter_account', 'ilike', search),
                       ]
        customers = ResPartner.sudo().search(domain)
        posts_count = len(customers)
        step = 50
        pager = portal_pager(
            url="/crm/customers/",
            total=posts_count,
            page=page,
            step=step
        )
        customers = customers[(page - 1) * step:page * step]
        values = {
            'pager': pager,
            'customers': customers,
            'search': search,
        }
        return http.request.render('crm_social_profile.customer_crm_index', {
            'values': values,
        })