# coding: utf-8
from datetime import datetime

from odoo import fields, models
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class ResUser(models.Model):
    _name = "res.users"
    _inherit = ["res.users", "gitlab.mixin.connection"]

    git_id = fields.Char(readonly=True)
    username = fields.Char(string="Username in Gitlab")
    state_git = fields.Char(readonly=True)
    avatar_url = fields.Char(readonly=True)
    web_url = fields.Char(readonly=True)
    sync_last_date = fields.Datetime(readonly=True)

    def _get_info_all_user(self):
        """This method return a dictionary with info related with users registered in gitlab"""
        base_url = self._get_gitlab_url()
        if base_url:
            url_users = f"{base_url}users/"
            info_user = self.get_response_url(url_users)
            if info_user is False:
                raise ValidationError("Users Not Found in Gitlab")
            if "message" not in info_user.keys():
                return info_user

    # GET /projects/:id/issues?username=name
    @staticmethod
    def _get_issues_by_username(self, project_id=""):
        if isinstance(project_id, str) and project_id != "":
            base_url = self._get_gitlab_url()
            url_user = f"{base_url}projects/{project_id}issues?username={self.username}"
            info_issues = self.get_response_url(url_user)
            if isinstance(info_issues, list):
                return info_issues
        return False

    def update_task_assigned(self):
        # TODO update field user_ids [los asignados] a esa tarea
        pass

    # GET /users?username=name
    def _get_info_by_username(self, username=""):
        base_url = self._get_gitlab_url()
        if isinstance(self.username, str) and self.username != "":
            url_user = f"{base_url}users?/username={self.username}"
            info_user = self.get_response_url(url_user)
            if isinstance(info_user, list) and len(info_user) > 0:
                return info_user
            else:
                raise ValidationError("User %s not found" % self.username)
        return False

    def return_info_by_username(self, username=""):
        base_url = self._get_gitlab_url()
        if isinstance(username, str) and username != "":
            url_user = f"{base_url}users/?username={username}"
            info_user = self.get_response_url(url_user)
            if isinstance(info_user, list) and len(info_user) > 0:
                return info_user
            else:
                raise ValidationError("User %s not found" % username)
        return False

    def make_sync_user(self, sync_user):
        if sync_user and isinstance(sync_user, list):  # if the user exist the update
            data_syn = {
                "username": sync_user[0]["username"],
                "git_id": sync_user[0]["id"],
                "state_git": sync_user[0]["state"],
                "avatar_url": sync_user[0]["avatar_url"],
                "web_url": sync_user[0]["web_url"],
                "sync_last_date": datetime.now(),
            }
            self.sudo().write(data_syn)
        else:
            return dict(
                message="Error sync! User not found",
            )

    def action_sync_user_data(self):
        """Allows to sync data for the user obtained by gitlab api"""
        sync_user = self._get_info_by_username()
        self.make_sync_user(sync_user)
        # self.action_sync_issues_list()  # run sync method for update the issues

    def action_sync_issues_list(self):
        sync_issues = self._get_issues_by_project()
        self.make_sync_issues(sync_issues)

    def make_sync_issues(self, sync_issues):
        if sync_issues and len(sync_issues) > 0:  # if the projects has issues
            for obj_sync in sync_issues:
                if "id" in obj_sync:
                    self.create_or_update_issue(obj_sync)
                else:
                    _logger.info("message request %s " % obj_sync)
        else:
            return dict(
                message="Error sync! List not found",
            )
