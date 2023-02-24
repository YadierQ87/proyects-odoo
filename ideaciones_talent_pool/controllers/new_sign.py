# -*- coding: utf-8 -*-

import logging
import werkzeug
import odoo
from odoo import http, _
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import Home
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError
from odoo.http import request
from odoo import http, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class AuthSignupHome(AuthSignupHome):
    def send_mail(self, email):
        template = request.env.ref('ideaciones_talent_pool.ideaciones_mail_template_register')
        User = request.env['res.users']
        user_sudo = User.sudo().search(
            User._get_login_domain(email), order=User._get_login_order(), limit=1
        )
        if template and user_sudo:
            template.email_to = email
            template.sudo().send_mail(user_sudo.id, force_send=True)
            _logger.info("Email sent to %s", email)

    def send_admin_notification(self):
        template = request.env.ref('ideaciones_talent_pool.ideaciones_mail_admin_notification')
        if template:
            template.sudo().send_mail(force_send=True)

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in (
            'login', 'name', 'password',
            'type_partner', 'title',
            'lastname', 'job_title', 'interested',
            'type_contact', 'country_id',
            'preferences', 'sex', 'passport', 'ci_number'
        )}
        if qcontext.get('country_id'):
            values.update({'country_id': int(qcontext.get('country_id'))})
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if len(qcontext.get('ci_number')) > 12:
            raise UserError(_("El Ci no puede ser mayor de 12 dígitos"))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
            raise UserError(_("Another user is already registered using this email address."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '').split('_')[0]
        if lang in supported_lang_codes:
            values['lang'] = lang
        # end of create entity
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('ideaciones_talent_pool.ideaciones_mail_template_register',
                                           raise_if_not_found=False).sudo()
                if user_sudo and template:
                    values = template.generate_email(user_sudo.partner_id.id, ['body_html', 'email_from', 'subject'])
                    values['mail_server_id'] = request.env['ir.mail_server'].sudo().search([], limit=1).id
                    values['email_to'] = user_sudo.partner_id.email
                    mail_mail_obj = request.env['mail.mail']
                    msg_id = mail_mail_obj.sudo().create(values)
                    if msg_id:
                        mail_mail_obj.sudo().send([msg_id])
                    _logger.info("Template %s", template)
                # self.send_mail(qcontext.get('login'))  # send email
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account. %s" % e)
        response = request.render(
            'ideaciones_talent_pool.page_for_register',
            qcontext
        )
        if qcontext.get("type_contact") == 'cliente':
            response = request.render(
                'ideaciones_talent_pool.ice_create_client_template',
                qcontext
            )
        if qcontext.get("type_contact") == 'colaborador':
            response = request.render(
                'ideaciones_talent_pool.ice_create_talent_template',
                qcontext
            )
        response.headers['X-Frame-Options'] = 'DENY'
        return response
