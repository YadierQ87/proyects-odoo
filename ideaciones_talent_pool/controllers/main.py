import json
import logging

_logger = logging.getLogger(__name__)

from datetime import datetime
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.web.controllers.main import Home
from odoo import http, SUPERUSER_ID, _
from ..models.res_partner import PartnerValidator
from odoo.http import request
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError, AccessDenied
import werkzeug
import base64


class Website(Home):
    @http.route()
    def index(self, *args, **kw):
        countries = request.env["res.country"].sudo().search([])
        titles = request.env["res.partner.title"].sudo().search([])
        # redirect all the website for my dashboard if user logged in
        if request.session.uid:
            return werkzeug.utils.redirect('/my')
        else:
            return http.request.render(
                'ideaciones_talent_pool.custom_landing_ideaciones',
                {
                    'titles': titles,
                    'countries': countries,
                }
            )


class TalentPool(WebsiteForm):
    # rewrite the route for default home
    @http.route(['/', '/home'], type='http', auth="public", website=True, sitemap=True)
    def index(self, **kwargs):
        countries = request.env["res.country"].sudo().search([])
        titles = request.env["res.partner.title"].sudo().search([])
        # redirect all the website for my dashboard if user logged in
        if request.session.uid:
            return werkzeug.utils.redirect('/my')
        else:
            return http.request.render(
                'ideaciones_talent_pool.custom_landing_ideaciones',
                {
                    'titles': titles,
                    'countries': countries,
                }
            )

    # asking for web/signup when you're logged in
    @http.route(['/add/talent'], type='http', auth="public", website=True, sitemap=True)
    def the_talent_signup(self, **kwargs):
        # redirect all the website for my dashboard if user logged in
        if request.session.uid:
            return werkzeug.utils.redirect('/my')
        else:
            return http.request.render(
                'ideaciones_talent_pool.ice_create_talent_template',
            )

    @http.route(['/add/client'], type='http', auth="public", website=True, sitemap=True)
    def the_client_signup(self, **kwargs):
        # redirect all the website for my dashboard if user logged in
        if request.session.uid:
            return werkzeug.utils.redirect('/my')
        else:
            return http.request.render(
                'ideaciones_talent_pool.ice_create_client_template',
            )

    @http.route(['/my/cv'], type='http', auth="user", website=True, sitemap=True)
    def the_client_signup(self, **kwargs):
        partner_id = request.env.user.partner_id.id
        res_partner = request.env['res.partner'].sudo().browse(partner_id)
        project_count = request.env['project.project'].search_count([])  # todo domain for user
        task_count = request.env['project.task'].search_count([])
        return http.request.render(
            'ideaciones_talent_pool.template_summary_cv',
            {
                'partner': res_partner,
                'project_count': project_count,
                'task_count': task_count,

            }
        )

    # /update/client old , now is /update/partner
    @http.route(['/update/partner'], type="http", auth="user",
                website=True, method=['POST'], csrf=False)
    def form_update_client(self, **post):
        ret = {}
        partner_id = request.env.user.partner_id.id
        res_partner = request.env['res.partner'].sudo().browse(partner_id)
        validator_list = {}
        post_copy = post.copy()
        for key, value in post_copy.items():
            if "#()#" in key:
                split_key = key.split("#()#")
                validator_type = split_key[0]
                field_name = split_key[1]
                validator_list.update({
                    field_name: validator_type
                })
                post[field_name] = post.pop(key)
        partner_validator = PartnerValidator()
        errors = partner_validator.validate(post, validator_list)
        if len(errors):
            ret['errors'] = errors
            return json.dumps(ret)
        values = {
            "name": post.get('name'),
            "type": 'contact',
            "welcome": 1,
        }
        preferences = []
        aux = []
        result = ''
        if post.get("Teléfono"):
            preferences.append("Teléfono")
            contact = request.env["res.preference.contact"].sudo().search(
                [
                    ('id', '=', request.env.ref('ideaciones_talent_pool.res_preference_telefono').id)
                ], limit=1)
            aux.append(contact.id)
        if post.get("Correo"):
            preferences.append("Correo")
            contact = request.env["res.preference.contact"].sudo().search(
                [
                    ('id', '=', request.env.ref('ideaciones_talent_pool.res_preference_correo').id)
                ], limit=1)
            aux.append(contact.id)
        if post.get("Zoom"):
            preferences.append("Zoom")
            contact = request.env["res.preference.contact"].sudo().search(
                [
                    ('id', '=', request.env.ref('ideaciones_talent_pool.res_preference_zoom').id)
                ], limit=1)
            aux.append(contact.id)
        if post.get("Telegram"):
            preferences.append("Telegram")
            contact = request.env["res.preference.contact"].sudo().search(
                [
                    ('id', '=', request.env.ref('ideaciones_talent_pool.res_preference_telegram').id)
                ], limit=1)
            aux.append(contact.id)
        if post.get("Linkedin"):
            preferences.append("Linkedin")
            contact = request.env["res.preference.contact"].sudo().search(
                [
                    ('id', '=', request.env.ref('ideaciones_talent_pool.res_preference_linkedin').id)
                ], limit=1)
            aux.append(contact.id)
        if post.get("Whatsapp"):
            preferences.append("Whatsapp")
            contact = request.env["res.preference.contact"].sudo().search(
                [
                    ('id', '=', request.env.ref('ideaciones_talent_pool.res_preference_whatsapp').id)
                ], limit=1)
            aux.append(contact.id)
        _logger.info("Preferences PARTNER %s" % preferences)
        if post.get('title') != "" and post.get('title'):
            values["title"] = int(post.get('title'))
        if post.get('country_id') != "" and post.get('country_id'):
            values["country_id"] = int(post.get('country_id'))
        if post.get('job_title') != "" and post.get('job_title'):
            values["job_title"] = post.get('job_title')
        if post.get('type_contact') != "" and post.get('type_contact'):
            values["type_contact"] = post.get('type_contact')
        if post.get('speciality') != "" and post.get('speciality'):
            values["speciality"] = post.get('speciality')
        if post.get('status_work') != "":
            values["status_work"] = post.get('status_work')
        if post.get('job_name') != "":
            values["job_name"] = post.get('job_name')
        if post.get('institution') != "":
            values["institution"] = post.get('institution')
        if post.get('ministery') != "":
            values["ministery"] = post.get('ministery')
        if post.get('lastname') != "":
            values["lastname"] = post.get('lastname')
        if post.get('sex') != "":
            values["sex"] = post.get('sex')
        if post.get('passport') != "":
            values["passport"] = post.get('passport')
        if post.get('ci_number') != "":
            values["ci_number"] = post.get('ci_number')
        if post.get('province') != "":
            values["province"] = post.get('province')
        if post.get('whatsapp') != "":
            values["whatsapp"] = post.get('whatsapp')
        if post.get('facebook') != "":
            values["facebook"] = post.get('facebook')
        if post.get('orcid') != "" and post.get('orcid'):
            values["orcid"] = post.get('orcid')
        if post.get('linkedin') != "" and post.get('linkedin'):
            values["linkedin"] = post.get('linkedin')
        if post.get('website_own') != "" and post.get('website_own'):
            values["website_own"] = post.get('website_own')
        if post.get('mobile') != "" and post.get('mobile'):
            values["mobile"] = post.get('mobile')
        if post.get('phone') != "" and post.get('phone'):
            values["phone"] = post.get('phone')
        if post.get('email') != "" and post.get('email'):
            values["email"] = post.get('email')
        if post.get('interested') != "" and post.get('interested'):
            values["interested"] = post.get('interested')
        if len(preferences) > 0:
            values["new_pref_contacts"] = ""
            for pref in preferences:
                if pref:
                    result += pref + " ; "
            if result:
                values["new_pref_contacts"] = result.rstrip(' ; ')
        if aux:
            values["pref_contact_ids"] = [(6, 0, aux)]
        if post.get('profile_pic'):
            for c_file in request.httprequest.files.getlist('profile_pic'):
                data = c_file.read()
                values["image_1920"] = base64.b64encode(data)
        if post.get('birthday') != "" and post.get('birthday'):
            convert = post.get('birthday')[0:10]  # 01/06/2022 12:25 AM DD/MM/YYYY
            split_birthday = convert.split("/")
            if len(split_birthday) > 1:
                great_birthday = split_birthday[2] + "-" + split_birthday[1] + "-" + split_birthday[0]
            else:
                great_birthday = post.get('birthday')
            birthday = datetime.strptime(great_birthday, '%Y-%m-%d').date()
            values["birthday"] = birthday
        try:
            for rec in res_partner:
                rec.with_user(SUPERUSER_ID).write(values)
            return werkzeug.utils.redirect('/success/msg')
        except (AccessError, MissingError, ValueError, ValidationError) as params:
            return werkzeug.utils.redirect('/error/message')

    # /update/curriculum
    @http.route(['/update/curriculum'], type="http", auth="user", website=True, method=['POST'], csrf=False)
    def form_update_curriculum(self, **post):
        partner_id = request.env.user.partner_id.id
        res_partner = request.env['res.partner'].sudo().browse(partner_id)
        values = {
            "summary_cv": post.get('summary_cv'),
        }
        try:
            for rec in res_partner:
                rec.with_user(SUPERUSER_ID).write(values)
            return werkzeug.utils.redirect('/success/msg')
        except (AccessError, MissingError, ValueError, ValidationError) as params:
            return werkzeug.utils.redirect('/error/message')

            # route for call api json titles
    @http.route(['/get/titles'], type='json', auth='public', methods=['POST'], website=True)
    def get_titles_json(self):
        titles = request.env["res.partner.title"].sudo().search([])
        result = list()
        for title in titles:
            result.append({"id": title.id, "shortcut": title.shortcut})
        return result

    # route for call api json countries
    @http.route(['/get/countries'], type='json', auth='public', methods=['POST'], website=True)
    def get_countries_json(self):
        countries = request.env["res.country"].sudo().search([])
        result = list()
        for country in countries:
            result.append({"id": country.id, "name": country.name})
        return result

    @http.route('/ideaciones/add/skill', type='json', auth='user', methods=['POST'], csrf=False)
    def add_skill(self, **post):
        skills_ids = post.get('tag_group_id').split(',')
        competence_id = request.env['res.partner.competences'].sudo().create({
            'specialty': request.env['res.partner.specialty'].sudo().create({
                'name': post.get('tag_id'),
            }).id,
            'skills_ids': [(0, 0, {'name': a}) for a in skills_ids],
            'partner_id': request.env.user.partner_id.id,
        })
        return {
            "message": "OK",
            "competence_id": competence_id.id,
        }

    @http.route('/ideaciones/update/skill', type='json',
                auth='user', methods=['POST'], csrf=False)
    def update_skill(self, **post):
        competence_id = request.env['res.partner.competences'].sudo().browse(int(post.get('competence_id')))
        competence_id.specialty.name = post.get('tag_id')
        skills_ids = post.get('tag_group_id').split(',')
        competence_id.write({
            'skills_ids': [(5, 0, 0)]
        })
        competence_id.write({
            'skills_ids': [(0, 0, {'name': a}) for a in skills_ids]
        })
        return {
            "message": "OK",
            "competence_id": competence_id.id,
        }

    @http.route('/ideaciones/delete/skill', type='json',
                auth='user', methods=['POST'], csrf=False)
    def delete_skill(self, **post):
        competence_id = int(post.get('competence_id'))
        request.env['res.partner.competences'].sudo().browse(competence_id).unlink()
        return {
            "message": "OK",
        }

    @http.route('/ideaciones/get_skills_modal_values', type='json',
                auth='user', methods=['POST'], csrf=False)
    def get_skills_modal_values(self, **post):
        competence_id = request.env['res.partner.competences'].sudo().browse(int(post.get('competence_id')))
        return {
            "specialty": competence_id.specialty.name,
            "skills_ids": ",".join([skill.name for skill in competence_id.skills_ids]),
        }

    # controllers for rpc experience
    @http.route('/ideaciones/get_experiences_modal_values', type='json',
                auth='user', methods=['POST'], csrf=False)
    def get_experiences_modal_values(self, **post):
        experience_id = request.env['res.partner.experience.line'].sudo().browse(int(post.get('experience_id')))
        return {
            "name": experience_id.name,
            "period": experience_id.period,
            "role_function": experience_id.role_function,
            "institution": experience_id.institution,
            "type": experience_id.type,
            "specialty_id": experience_id.specialty_id.name,
            "category_id": experience_id.category_id.id,
            "duration": experience_id.duration,
            "country_id": experience_id.country_id.id,
            "description": experience_id.description,
            "observations": experience_id.observations,
            "notes": experience_id.notes,
            "url_website": experience_id.url_website,
            "qty_credits": experience_id.qty_credits,
            "editorial": experience_id.editorial,
        }

    @http.route('/ideaciones/add/experience', type='json', auth='user', methods=['POST'], csrf=False)
    def add_experience(self, **post):
        values = {
            "name": post.get('name'),
            "period": post.get('period'),
            "role_function": post.get('role_function'),
            "institution": post.get('institution'),
            "type": post.get('type'),
            "duration": post.get('duration'),
            "description": post.get('description'),
            "observations": post.get('observations'),
            "notes": post.get('notes'),
            "url_website": post.get('url_website'),
            "qty_credits": post.get('qty_credits'),
            "editorial": post.get('editorial'),
            'partner_id': request.env.user.partner_id.id,
        }
        if post.get('specialty_id'):
            specialty_id = request.env['res.partner.specialty'].sudo().create({
                "name": post.get('specialty_id')
            }).id
            values["specialty_id"] = specialty_id  # res.partner.specialty
        if post.get('category_id'):
            values["category_id"] = post.get('category_id')  # cv.experience.category
        if post.get('country_id'):
            values["country_id"] = post.get('country_id')  # res.country
        experience_id = request.env['res.partner.experience.line'].sudo().create(values)
        return {
            "message": "OK",
            "experience_id": experience_id.id,
        }

    @http.route('/ideaciones/update/experience', type='json',
                auth='user', methods=['POST'], csrf=False)
    def update_experience(self, **post):
        experience_id = request.env['res.partner.experience.line'].sudo().browse(int(post.get('experience_id')))
        values = {
            "name": post.get('name'),
            "period": post.get('period'),
            "role_function": post.get('role_function'),
            "institution": post.get('institution'),
            "type": post.get('type'),
            # "specialty_id": post.get('specialty_id.name'), # res.partner.specialty
            # "category_id": post.get('category_id.name'), # cv.experience.category
            "duration": post.get('duration'),
            # "country_id": post.get('country_id.name'), # res.country
            "description": post.get('description'),
            "observations": post.get('observations'),
            "notes": post.get('notes'),
            "url_website": post.get('url_website'),
            "qty_credits": post.get('qty_credits'),
            "editorial": post.get('editorial'),
            'partner_id': request.env.user.partner_id.id,
        }
        experience_id.write(values)
        return {
            "message": "OK",
            "experience_id": experience_id.id,
        }

    @http.route('/ideaciones/delete/experience', type='json',
                auth='user', methods=['POST'], csrf=False)
    def delete_experience(self, **post):
        experience_id = int(post.get('experience_id'))
        request.env['res.partner.experience.line'].sudo().browse(experience_id).unlink()
        return {
            "message": "OK",
        }

    @http.route('/ideaciones/validate_phone', type='json', auth='user', csrf=False)
    def validate_phone(self, **post):
        return PartnerValidator().validate_phone(post.get('number'))
