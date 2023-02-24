from odoo import fields, models


# this is an issue in Gitlab
class TaskProjects(models.Model):
    _inherit = "project.task"

    is_sync = fields.Boolean(
        default=False, help="Show if the task is synced"
    )  # change to True when it is sync with gitlab
    sync_last_date = fields.Datetime()  # it is compute when task sync with gitlab
    git_id = fields.Char(string="Issue-id in gitlab")
    created_in_gitlab = fields.Boolean(default=False)
    iid_gitlab = fields.Char(string="Issue-iid in gitlab")
    project_git_id = fields.Char()
    state = fields.Selection(
        string="State",
        selection=[("opened", "opened"), ("active", "active"), ("closed", "closed")],
        required=False,
    )
    confidential = fields.Char()
    issue_type = fields.Char()
    labels = fields.Html()
    milestone = fields.Char()
    weight = fields.Char()
    has_tasks = fields.Boolean(string="Has subtasks", required=False)
    task_status = fields.Char("Task status")
    human_time_estimate = fields.Char("Time estimate")
    human_total_time_spent = fields.Char("Total Time spent")
