# coding: utf-8
{
    "name": "Gitlab Integration with odoo project",
    "summary": """
        Uses the gitlab api and a simple setup to sync your project data in Gitlab with Odoo Project.
        """,
    "description": """Get the real information about your organization, registered users and groups with your 
    projects and list of related issues""",
    "version": "1.0.0",
    "license": "AGPL-3",
    "author": "Yadier Abel De Quesada",
    "website": "",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/project_gitgroup_views.xml",
        "views/project_task_views.xml",
        "views/project_project_views.xml",
        "views/res_user_views.xml",
        "views/res_config_view.xml",
    ],
    "demo": ["data/user.xml"],
}
