# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# Copyright (c) 2018, Marcus Watkins <marwatk@marcuswatkins.net>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t

from ansible.module_utils.basic import missing_required_lib

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion

from urllib.parse import urljoin

import traceback


def _determine_list_all_kwargs(version) -> dict[str, t.Any]:
    gitlab_version = LooseVersion(version)
    if gitlab_version >= LooseVersion("4.0.0"):
        # 4.0.0 removed 'as_list'
        return {"iterator": True, "per_page": 100}
    elif gitlab_version >= LooseVersion("3.7.0"):
        # 3.7.0 added 'get_all'
        return {"as_list": False, "get_all": True, "per_page": 100}
    else:
        return {"as_list": False, "all": True, "per_page": 100}


GITLAB_IMP_ERR: str | None = None
try:
    import gitlab
    import requests

    HAS_GITLAB_PACKAGE = True
    list_all_kwargs = _determine_list_all_kwargs(gitlab.__version__)
except Exception:
    gitlab = None  # type: ignore
    GITLAB_IMP_ERR = traceback.format_exc()
    HAS_GITLAB_PACKAGE = False
    list_all_kwargs = {}


def auth_argument_spec(spec=None):
    arg_spec = dict(
        ca_path=dict(type="str"),
        api_token=dict(type="str", no_log=True),
        api_oauth_token=dict(type="str", no_log=True),
        api_job_token=dict(type="str", no_log=True),
    )
    if spec:
        arg_spec.update(spec)
    return arg_spec


def find_project(gitlab_instance, identifier):
    try:
        project = gitlab_instance.projects.get(identifier)
    except Exception:
        current_user = gitlab_instance.user
        try:
            project = gitlab_instance.projects.get(f"{current_user.username}/{identifier}")
        except Exception:
            return None

    return project


def find_group(gitlab_instance, identifier):
    try:
        group = gitlab_instance.groups.get(identifier)
    except Exception:
        return None

    return group


def ensure_gitlab_package(module, min_version=None):
    if not HAS_GITLAB_PACKAGE:
        module.fail_json(
            msg=missing_required_lib("python-gitlab", url="https://python-gitlab.readthedocs.io/en/stable/"),
            exception=GITLAB_IMP_ERR,
        )
    gitlab_version = gitlab.__version__
    if min_version is not None and LooseVersion(gitlab_version) < LooseVersion(min_version):
        module.fail_json(
            msg=(
                f"This module requires python-gitlab Python module >= {min_version} (installed version: "
                f"{gitlab_version}). Please upgrade python-gitlab to version {min_version} or above."
            )
        )


def gitlab_authentication(module, min_version=None):
    ensure_gitlab_package(module, min_version=min_version)

    gitlab_url = module.params["api_url"]
    validate_certs = module.params["validate_certs"]
    ca_path = module.params["ca_path"]
    gitlab_user = module.params["api_username"]
    gitlab_password = module.params["api_password"]
    gitlab_token = module.params["api_token"]
    gitlab_oauth_token = module.params["api_oauth_token"]
    gitlab_job_token = module.params["api_job_token"]

    verify = ca_path if validate_certs and ca_path else validate_certs

    try:
        # We can create an oauth_token using a username and password
        # https://docs.gitlab.com/ee/api/oauth2.html#authorization-code-flow
        if gitlab_user:
            data = {"grant_type": "password", "username": gitlab_user, "password": gitlab_password}
            resp = requests.post(urljoin(gitlab_url, "oauth/token"), data=data, verify=verify)
            resp_data = resp.json()
            gitlab_oauth_token = resp_data["access_token"]

        gitlab_instance = gitlab.Gitlab(
            url=gitlab_url,
            ssl_verify=verify,
            private_token=gitlab_token,
            oauth_token=gitlab_oauth_token,
            job_token=gitlab_job_token,
            api_version=4,
        )
        gitlab_instance.auth()
    except (gitlab.exceptions.GitlabAuthenticationError, gitlab.exceptions.GitlabGetError) as e:
        module.fail_json(msg=f"Failed to connect to GitLab server: {e}")
    except gitlab.exceptions.GitlabHttpError as e:
        module.fail_json(
            msg=(
                f"Failed to connect to GitLab server: {e}. GitLab remove Session API now "
                "that private tokens are removed from user API endpoints since version 10.2."
            )
        )

    return gitlab_instance


def filter_returned_variables(gitlab_variables):
    # pop properties we don't know
    existing_variables = [dict(x.attributes) for x in gitlab_variables]
    KNOWN = [
        "key",
        "value",
        "description",
        "masked",
        "hidden",
        "protected",
        "variable_type",
        "environment_scope",
        "raw",
    ]
    for item in existing_variables:
        for key in list(item.keys()):
            if key not in KNOWN:
                item.pop(key)
    return existing_variables


def vars_to_variables(vars, module):
    # transform old vars to new variables structure
    variables = list()
    for item, value in vars.items():
        if isinstance(value, (str, int, float)):
            variables.append(
                {
                    "name": item,
                    "value": str(value),
                    "description": None,
                    "masked": False,
                    "protected": False,
                    "hidden": False,
                    "raw": False,
                    "variable_type": "env_var",
                }
            )

        elif isinstance(value, dict):
            new_item = {
                "name": item,
                "value": value.get("value"),
                "description": value.get("description"),
                "masked": value.get("masked"),
                "hidden": value.get("hidden"),
                "protected": value.get("protected"),
                "raw": value.get("raw"),
                "variable_type": value.get("variable_type"),
            }

            if value.get("environment_scope"):
                new_item["environment_scope"] = value.get("environment_scope")

            variables.append(new_item)

        else:
            module.fail_json(msg="value must be of type string, integer, float or dict")

    return variables
