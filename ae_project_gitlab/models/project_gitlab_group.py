# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
import logging
import threading
from datetime import datetime

from odoo import fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class GitlabGroup(models.Model):
    """Mapping attributes from Group in Gitlab"""

    _name = "gitlab.group.profile"
    _inherit = "gitlab.mixin.connection"
    _description = "Gitlab Group Profile Copy"

    name = fields.Char(string="Name in Gitlab", readonly=True)
    git_id = fields.Char(required=True)  # Example id: 1386105
    web_url = fields.Char(readonly=True)
    path = fields.Char(readonly=True)
    description = fields.Char(readonly=True)
    visibility = fields.Char(readonly=True)
    avatar_url = fields.Char(readonly=True)
    sync_last_date = fields.Datetime(readonly=True)
    project_git_ids = fields.One2many(
        comodel_name="project.project",
        inverse_name="group_git_id",
        string="Gitlab Projects",
        required=False,
    )

    def ir_cron_sync_all_projects(self):
        projects = self.env['project.project'].search([("git_id", "!=", "")])  # get all projects in gitlab
        for project in projects:
            #   project.action_sync_project_data()
            threading.Thread(target=project.action_sync_project_data())

    def _get_info_by_group(self):
        """This method return a dictionary with info related with the group if exist his id in gitlab"""
        if isinstance(self.git_id, str) and self.git_id != "":
            base_url = self._get_gitlab_url()
            if base_url:
                url_group = f"{base_url}groups/{self.git_id}"
                info_group = self.get_response_url(url_group)
                _logger.info(" INFO GROUP %s" % url_group)
                if info_group is False:
                    raise ValidationError("Group with ID %s Not Found" % self.git_id)
                return info_group
        return False

    # update sync data
    def make_sync_data(self, sync_group: dict):
        if sync_group and isinstance(sync_group, dict):
            self.name = sync_group["name"]
            self.description = sync_group["description"]
            self.web_url = sync_group["web_url"]
            self.avatar_url = sync_group["avatar_url"]
            self.visibility = sync_group["visibility"]
            self.path = sync_group["path"]
            self.sync_last_date = datetime.now()
        else:
            return dict(
                message="Error sync! Group not found",
            )

    # sync data for the group
    def action_sync_group_gitlab(self):
        """Allows to sync data for the group obtained by gitlab api"""
        sync_group = self._get_info_by_group()
        _logger.info("CONSOLE SYNC GROUP %s" % sync_group)
        if sync_group:
            self.make_sync_data(sync_group)
            # run method that sync list of projects
            if sync_group["projects"]:
                self.action_sync_project_list(sync_group["projects"])
            # run method that sync list of members
            sync_members = self._get_info_all_members()
            if sync_members:
                self.action_sync_member_list(sync_members)
        else:
            raise ValidationError("Groups %s Not Found" % self.git_id)

    def create_or_update_member(self, obj_member):
        ResUser = self.env["res.users"]
        find_user = ResUser.search([("git_id", "=", obj_member["id"])])
        # https://elgit.transgenia.org/api/v4/users/?username=efrain.carreon
        # get "email": "efrain.carreon@transgenia.org",
        user_gitlab = ResUser.return_info_by_username(obj_member["username"])
        data_syn = {
            "git_id": obj_member["id"],
            "login": user_gitlab[0]["email"],
            "username": obj_member["username"],
            "name": obj_member["name"],
            "state_git": obj_member["state"],
            "avatar_url": obj_member["avatar_url"],
            "web_url": obj_member["web_url"],
            "sync_last_date": datetime.now(),
        }
        if find_user:
            return find_user.update(data_syn)
        else:
            return ResUser.create(data_syn)

    def create_or_update_project(self, obj_project):
        ProjectProject = self.env["project.project"]
        find_project = ProjectProject.search([("git_id", "=", obj_project["id"])])
        data_syn = {
            "name": obj_project["name"],
            "git_id": obj_project["id"],
            "description": obj_project["description"],
            "name_with_namespace": obj_project["name_with_namespace"],
            "web_url": obj_project["web_url"],
            "readme_url": obj_project["readme_url"],
            "path": obj_project["path"],
            "path_with_namespace": obj_project["path_with_namespace"],
            "group_git_id": self.id,
            "sync_last_date": datetime.now(),
        }
        # if project.project already exist update and sync
        if find_project:
            find_project.update(data_syn)
            find_project.action_sync_project_data()
        # else create project.project and sync his data
        else:
            project_git = ProjectProject.create(data_syn)
            project_git.action_sync_project_data()
            self.project_git_ids |= project_git

    def action_sync_project_list(self, sync_projects):
        """get the list of projects related and create or update as project.project"""
        # if the group has projects
        if sync_projects and isinstance(sync_projects, list) > 0:
            for obj_proj in sync_projects:
                self.create_or_update_project(obj_proj)

    # TODO sync usuarios
    def _get_info_all_members(self):
        """This method return a dictionary with info related with the members in that group in gitlab"""
        if isinstance(self.git_id, str) and self.git_id != "":
            base_url = self._get_gitlab_url()
            if base_url:
                url_members = f"{base_url}groups/{self.git_id}/members"
                list_members = self.get_response_url(url_members)
                if list_members is False:
                    raise ValidationError("Members Not Found")
                else:
                    return list_members
        return False

    def action_sync_member_list(self, sync_members):
        """get the list of projects related and create or update as project.project"""
        # if the group has projects
        if sync_members and isinstance(sync_members, list) > 0:
            for obj_member in sync_members:
                self.create_or_update_member(obj_member)
