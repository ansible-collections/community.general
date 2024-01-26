# -*- coding: utf-8 -*-

# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# Copyright (c) 2018, Marcus Watkins <marwatk@marcuswatkins.net>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import missing_required_lib
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.six import integer_types, string_types

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin  # Python 3+

import traceback

GITLAB_IMP_ERR = None
try:
    import gitlab
    import requests
    HAS_GITLAB_PACKAGE = True
except Exception:
    gitlab = None
    GITLAB_IMP_ERR = traceback.format_exc()
    HAS_GITLAB_PACKAGE = False


def auth_argument_spec(spec=None):
    arg_spec = (dict(
        ca_path=dict(type='str'),
        api_token=dict(type='str', no_log=True),
        api_oauth_token=dict(type='str', no_log=True),
        api_job_token=dict(type='str', no_log=True),
    ))
    if spec:
        arg_spec.update(spec)
    return arg_spec


def find_project(gitlab_instance, identifier):
    try:
        project = gitlab_instance.projects.get(identifier)
    except Exception as e:
        current_user = gitlab_instance.user
        try:
            project = gitlab_instance.projects.get(current_user.username + '/' + identifier)
        except Exception as e:
            return None

    return project


def find_group(gitlab_instance, identifier):
    try:
        group = gitlab_instance.groups.get(identifier)
    except Exception as e:
        return None

    return group


def ensure_gitlab_package(module):
    if not HAS_GITLAB_PACKAGE:
        module.fail_json(
            msg=missing_required_lib("python-gitlab", url='https://python-gitlab.readthedocs.io/en/stable/'),
            exception=GITLAB_IMP_ERR
        )


def gitlab_authentication(module):
    ensure_gitlab_package(module)

    gitlab_url = module.params['api_url']
    validate_certs = module.params['validate_certs']
    ca_path = module.params['ca_path']
    gitlab_user = module.params['api_username']
    gitlab_password = module.params['api_password']
    gitlab_token = module.params['api_token']
    gitlab_oauth_token = module.params['api_oauth_token']
    gitlab_job_token = module.params['api_job_token']

    verify = ca_path if validate_certs and ca_path else validate_certs

    try:
        # python-gitlab library remove support for username/password authentication since 1.13.0
        # Changelog : https://github.com/python-gitlab/python-gitlab/releases/tag/v1.13.0
        # This condition allow to still support older version of the python-gitlab library
        if LooseVersion(gitlab.__version__) < LooseVersion("1.13.0"):
            gitlab_instance = gitlab.Gitlab(url=gitlab_url, ssl_verify=verify, email=gitlab_user, password=gitlab_password,
                                            private_token=gitlab_token, api_version=4)
        else:
            # We can create an oauth_token using a username and password
            # https://docs.gitlab.com/ee/api/oauth2.html#authorization-code-flow
            if gitlab_user:
                data = {'grant_type': 'password', 'username': gitlab_user, 'password': gitlab_password}
                resp = requests.post(urljoin(gitlab_url, "oauth/token"), data=data, verify=verify)
                resp_data = resp.json()
                gitlab_oauth_token = resp_data["access_token"]

            gitlab_instance = gitlab.Gitlab(url=gitlab_url, ssl_verify=verify, private_token=gitlab_token,
                                            oauth_token=gitlab_oauth_token, job_token=gitlab_job_token, api_version=4)

        gitlab_instance.auth()
    except (gitlab.exceptions.GitlabAuthenticationError, gitlab.exceptions.GitlabGetError) as e:
        module.fail_json(msg="Failed to connect to GitLab server: %s" % to_native(e))
    except (gitlab.exceptions.GitlabHttpError) as e:
        module.fail_json(msg="Failed to connect to GitLab server: %s. \
            GitLab remove Session API now that private tokens are removed from user API endpoints since version 10.2." % to_native(e))

    return gitlab_instance


def filter_returned_variables(gitlab_variables):
    # pop properties we don't know
    existing_variables = [dict(x.attributes) for x in gitlab_variables]
    KNOWN = ['key', 'value', 'masked', 'protected', 'variable_type', 'environment_scope', 'raw']
    for item in existing_variables:
        for key in list(item.keys()):
            if key not in KNOWN:
                item.pop(key)
    return existing_variables


def vars_to_variables(vars, module):
    # transform old vars to new variables structure
    variables = list()
    for item, value in vars.items():
        if isinstance(value, (string_types, integer_types, float)):
            variables.append(
                {
                    "name": item,
                    "value": str(value),
                    "masked": False,
                    "protected": False,
                    "raw": False,
                    "variable_type": "env_var",
                }
            )

        elif isinstance(value, dict):
            new_item = {
                "name": item,
                "value": value.get('value'),
                "masked": value.get('masked'),
                "protected": value.get('protected'),
                "raw": value.get('raw'),
                "variable_type": value.get('variable_type'),
            }

            if value.get('environment_scope'):
                new_item['environment_scope'] = value.get('environment_scope')

            variables.append(new_item)

        else:
            module.fail_json(msg="value must be of type string, integer, float or dict")

    return variables
