{
    "name": "Ideaciones talent pool",
    "summary": """
        Create talent pool as collaborators in projects from crm leads""",
    "version": "1.3",
    "license": "AGPL-3",
    "author": "Yadier Abel De Quesada",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "project",
        "website",
        "website_form",
        "crm",
        "ideaciones_theme",
        "website_fancybox",
    ],
    "qweb": [
        # "static/src/xml/website_popup_profile.xml",
    ],
    "data": [
        # templates for website
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/website_templates_inherit.xml",
        "views/website_layout.xml",
        # old templates
        "views/client_templates.xml",
        "views/talent_templates.xml",
        "views/profile_templates.xml",
        "views/website_pages.xml",
        # views for backend
        "views/crm_leads_views.xml",
        "views/project_project_views.xml",
        "views/res_partner_view.xml",
        # data
        "data/curriculum.xml",
        "data/data_forms.xml",
        "data/mail_data.xml",
        "data/settings.xml",
    ],
    "demo": [],
    "external_dependencies": {
        "python": ["phonenumbers", "validators"],
    },
}
