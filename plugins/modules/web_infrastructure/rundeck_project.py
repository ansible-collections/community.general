#!/usr/bin/python
# -*- coding: utf-8 -*-

# Ansible module to manage rundeck projects
# (c) 2017, Loic Blot <loic.blot@unix-experience.fr>
# Sponsored by Infopro Digital. http://www.infopro-digital.com/
# Sponsored by E.T.A.I. http://www.etai.fr/
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: rundeck_project

short_description: Manage Rundeck projects.
description:
    - Create and remove Rundeck projects through HTTP API.
author: "Loic Blot (@nerzhul)"
options:
    state:
        description:
            - Create or remove Rundeck project.
        choices: ['present', 'absent']
        default: 'present'
    name:
        description:
            - Sets the project name.
        required: True
    url:
        description:
            - Sets the rundeck instance URL.
        required: True
    api_version:
        description:
            - Sets the API version used by module.
            - API version must be at least 14.
        default: 14
    token:
        description:
            - Sets the token to authenticate against Rundeck API.
        required: True
    client_cert:
        version_added: '0.2.0'
    client_key:
        version_added: '0.2.0'
    force:
        version_added: '0.2.0'
    force_basic_auth:
        version_added: '0.2.0'
    http_agent:
        version_added: '0.2.0'
    url_password:
        version_added: '0.2.0'
    url_username:
        version_added: '0.2.0'
    use_proxy:
        version_added: '0.2.0'
    validate_certs:
        version_added: '0.2.0'
extends_documentation_fragment: url
'''

EXAMPLES = '''
- name: Create a rundeck project
  community.general.rundeck_project:
    name: "Project_01"
    api_version: 18
    url: "https://rundeck.example.org"
    token: "mytoken"
    state: present

- name: Remove a rundeck project
  community.general.rundeck_project:
    name: "Project_02"
    url: "https://rundeck.example.org"
    token: "mytoken"
    state: absent
'''

RETURN = '''
rundeck_response:
    description: Rundeck response when a failure occurs
    returned: failed
    type: str
before:
    description: dictionary containing project information before modification
    returned: success
    type: dict
after:
    description: dictionary containing project information after modification
    returned: success
    type: dict
'''

# import module snippets
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible.module_utils.urls import fetch_url, url_argument_spec
import json


class RundeckProjectManager(object):
    def __init__(self, module):
        self.module = module

    def handle_http_code_if_needed(self, infos):
        if infos["status"] == 403:
            self.module.fail_json(msg="Token not allowed. Please ensure token is allowed or has the correct "
                                      "permissions.", rundeck_response=infos["body"])
        elif infos["status"] >= 500:
            self.module.fail_json(msg="Fatal Rundeck API error.", rundeck_response=infos["body"])

    def request_rundeck_api(self, query, data=None, method="GET"):
        resp, info = fetch_url(self.module,
                               "%s/api/%d/%s" % (self.module.params["url"], self.module.params["api_version"], query),
                               data=json.dumps(data),
                               method=method,
                               headers={
                                   "Content-Type": "application/json",
                                   "Accept": "application/json",
                                   "X-Rundeck-Auth-Token": self.module.params["token"]
                               })

        self.handle_http_code_if_needed(info)
        if resp is not None:
            resp = resp.read()
            if resp != "":
                try:
                    json_resp = json.loads(resp)
                    return json_resp, info
                except ValueError as e:
                    self.module.fail_json(msg="Rundeck response was not a valid JSON. Exception was: %s. "
                                              "Object was: %s" % (to_native(e), resp))
        return resp, info

    def get_project_facts(self):
        resp, info = self.request_rundeck_api("project/%s" % self.module.params["name"])
        return resp

    def create_or_update_project(self):
        facts = self.get_project_facts()
        if facts is None:
            # If in check mode don't create project, simulate a fake project creation
            if self.module.check_mode:
                self.module.exit_json(changed=True, before={}, after={"name": self.module.params["name"]})

            resp, info = self.request_rundeck_api("projects", method="POST", data={
                "name": self.module.params["name"],
                "config": {}
            })

            if info["status"] == 201:
                self.module.exit_json(changed=True, before={}, after=self.get_project_facts())
            else:
                self.module.fail_json(msg="Unhandled HTTP status %d, please report the bug" % info["status"],
                                      before={}, after=self.get_project_facts())
        else:
            self.module.exit_json(changed=False, before=facts, after=facts)

    def remove_project(self):
        facts = self.get_project_facts()
        if facts is None:
            self.module.exit_json(changed=False, before={}, after={})
        else:
            # If not in check mode, remove the project
            if not self.module.check_mode:
                self.request_rundeck_api("project/%s" % self.module.params["name"], method="DELETE")
            self.module.exit_json(changed=True, before=facts, after={})


def main():
    # Also allow the user to set values for fetch_url
    argument_spec = url_argument_spec()
    argument_spec.update(dict(
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        name=dict(required=True, type='str'),
        url=dict(required=True, type='str'),
        api_version=dict(type='int', default=14),
        token=dict(required=True, type='str', no_log=True),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    if module.params["api_version"] < 14:
        module.fail_json(msg="API version should be at least 14")

    rundeck = RundeckProjectManager(module)
    if module.params['state'] == 'present':
        rundeck.create_or_update_project()
    elif module.params['state'] == 'absent':
        rundeck.remove_project()


if __name__ == '__main__':
    main()
