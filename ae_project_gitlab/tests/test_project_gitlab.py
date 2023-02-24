# coding: utf-8

import json
import pkgutil

from odoo.tests.common import TransactionCase

_TEST_URL = "https://gitlab.com/api/v4/projects"


class TestGitlabConnection(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestGitlabConnection, self).setUp(*args, **kwargs)
        git_config = self.env["res.config.settings"].sudo()
        git_config.create({"gitlab_api_url": _TEST_URL})
        git_config.set_values()
        self.test_group = self.env["gitlab.group.profile"].create(
            {
                "name": "Odoo Business Unit",
                "git_id": 788100,
                "description": "Description About the Group",
                "visibility": "private",
            }
        )
        self.test_project = self.env["project.project"].create(
            {
                "name": "Odoo Ce Project",
                "git_id": False,
                "description": "Project for Odoo",
            }
        )
        self.test_user = self.env["res.users"].sudo().search([], limit=1)
        self.test_issue = self.env["project.task"].create(
            {
                "name": "New testing issue",
                "project_id": self.test_project.id,
                "git_id": "909",
            }
        )

    # testing information group in demo data json
    def test_get_info_by_group(self):
        group = json.loads(
            pkgutil.get_data(self.__module__, "group_response.json").decode("utf-8")
        )
        self.assertIsInstance(group, dict)
        self.assertNotEqual(group["description"], self.test_group.description)
        self.test_group.update(
            {"description": "Description About the Group v2", "git_id": 185}
        )
        self.test_group.make_sync_data(group)  # call sync using json info
        self.assertEqual(group["description"], self.test_group.description)
        self.assertEqual(str(group["id"]), self.test_group.git_id)
        self.assertEqual(self.test_group.name, "Odoo TESTING Unit")

    # testing information project in demo data json
    def test_get_info_by_project(self):
        project = json.loads(
            pkgutil.get_data(self.__module__, "project_response.json").decode("utf-8")
        )
        self.assertIsInstance(project, dict)
        self.assertFalse(self.test_project._get_issues_by_project())
        self.assertEqual(project["name"], self.test_project.name)
        self.assertNotEqual(project["description"], self.test_project.description)
        self.test_project.update({"description": "Project for Odoo Gitlab v2"})
        self.assertEqual(project["description"], self.test_project.description)
        self.test_project.make_sync_project(project)  # sync data from json
        self.assertEqual(self.test_project.name, "Odoo Ce Project")

    # testing information user in demo data json
    def test_get_info_by_user(self):
        user = json.loads(
            pkgutil.get_data(self.__module__, "user_response.json").decode("utf-8")
        )
        self.assertIsInstance(user, list)
        self.test_user.make_sync_user(user)
        self.assertEqual(self.test_user.username, user[0]["username"])
        self.assertEqual(self.test_user.state_git, "active")

    #  testing info issues in demo data json
    def test_get_project_issues(self):
        """testing a list of issues"""

        issues = json.loads(
            pkgutil.get_data(self.__module__, "issues_response.json").decode("utf-8")
        )
        self.assertEqual(self.test_issue.name, "New testing issue")
        self.test_project.update({"git_id": 101})
        self.test_project.make_sync_issues(issues)
        for issue in self.test_project.task_ids:
            self.assertNotEqual(issue.name, False)
            self.assertEqual(issue.state, "opened")
            self.assertEqual(issue.project_id.git_id, self.test_project.git_id)
