# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
import json

import requests as requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from odoo import fields, models, api
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

_CODE_404 = 404  # response is not found
_CODE_401 = 401   # response Token is expired
_CODE_200 = 200  # response is successful


class GitlabConnection(models.AbstractModel):
    _name = "gitlab.mixin.connection"
    _description = "Gitlab Mixin Connection"

    gh_session = requests.Session()

    def _get_connection(self):
        self.gh_session = requests.Session()

    def _close_connection(self):
        self.gh_session.close()

    def _get_gitlab_url(self):
        env_gitlab_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ae_project_gitlab.gitlab_api_url")
        )
        if env_gitlab_url:
            return env_gitlab_url
        raise ValidationError("Gitlab api url is missing! Please configure in Settings")

    def get_response_url(self, url):
        token = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ae_project_gitlab.gitlab_secret_token")
        )
        gitlab_url = self._get_gitlab_url()
        if token and isinstance(gitlab_url, str):
            if isinstance(url, str) and gitlab_url in url:
                try:
                    response_git = self.gh_session.get(
                        url, headers={"PRIVATE-TOKEN": token}, timeout=30, verify=False
                    )
                    if response_git.status_code == _CODE_404:
                        raise ValidationError("Response %s data not found" % _CODE_404)
                    if response_git.status_code == _CODE_401:
                        raise ValidationError("Error %s Token is expired" % _CODE_401)
                    elif response_git.status_code == _CODE_200:
                        return json.loads(response_git.text)
                except requests.ConnectionError as ex:
                    raise ValidationError("Connection Error: %s" % ex)
            else:
                return False
        else:
            raise ValidationError(
                "Gitlab config is missing! Please configure it in Settings"
            )


# Enable features in the res.config.settings [gitlab.system.config]
class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    gitlab_secret_token = fields.Char(string="Gitlab Secret Token")
    gitlab_api_url = fields.Char(string="Gitlab Base Api Url")

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        configuration = self.env["ir.config_parameter"].sudo()
        configuration.set_param(
            "ae_project_gitlab.gitlab_secret_token", self.gitlab_secret_token
        )
        configuration.set_param("ae_project_gitlab.gitlab_api_url", self.gitlab_api_url)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        value_token = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ae_project_gitlab.gitlab_secret_token")
        )
        value_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ae_project_gitlab.gitlab_api_url")
        )
        res.update({"gitlab_secret_token": value_token})
        res.update({"gitlab_api_url": value_url})
        return res
