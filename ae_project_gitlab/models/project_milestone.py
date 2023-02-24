from odoo import fields, models, api


# Milestones
# Milestones in GitLab are a way to track issues and merge requests created to achieve
# a broader goal in a certain period of time.

class ModelName(models.Model):
    _inherit = 'project.milestone'
    _description = 'Milestone for the Project used in Gitlab'

    name = fields.Char()
    is_sync = fields.Boolean(
        default=False, help="Show if the task is synced"
    )  # change to True when it is sync with gitlab
    sync_last_date = fields.Datetime()  # it is compute when task sync with gitlab
    git_id = fields.Char(string="Milestone-id in gitlab")
    created_in_gitlab = fields.Boolean(default=False)
    iid_gitlab = fields.Char(string="Issue-iid in gitlab")
    project_git_id = fields.Char()
    description = fields.Html()
    state = fields.Char()
    expired = fields.Boolean()
    web_url = fields.Char()
