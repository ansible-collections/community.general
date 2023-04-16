#!/usr/bin/python
# -*- coding: utf-8 -*-

# Ansible module to manage rundeck projects
# Copyright (c) 2017, Loic Blot <loic.blot@unix-experience.fr>
# Sponsored by Infopro Digital. http://www.infopro-digital.com/
# Sponsored by E.T.A.I. http://www.etai.fr/
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: rundeck_project

short_description: Manage Rundeck projects
description:
    - Create and remove Rundeck projects through HTTP API.
author: "Loic Blot (@nerzhul)"
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
options:
    state:
        type: str
        description:
            - Create or remove Rundeck project.
        choices: ['present', 'absent']
        default: 'present'
    name:
        type: str
        description:
            - Sets the project name.
        required: true
    api_token:
        description:
            - Sets the token to authenticate against Rundeck API.
        aliases: ["token"]
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
extends_documentation_fragment:
  - ansible.builtin.url
  - community.general.attributes
  - community.general.rundeck
'''

EXAMPLES = '''
- name: Create a rundeck project
  community.general.rundeck_project:
    name: "Project_01"
    label: "Project 01"
    description: "My Project 01"
    url: "https://rundeck.example.org"
    api_version: 39
    api_token: "mytoken"
    state: present

- name: Remove a rundeck project
  community.general.rundeck_project:
    name: "Project_01"
    url: "https://rundeck.example.org"
    api_token: "mytoken"
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
from ansible_collections.community.general.plugins.module_utils.rundeck import (
    api_argument_spec,
    api_request,
)


class RundeckProjectManager(object):
    def __init__(self, module):
        self.module = module

    def get_project_facts(self):
        resp, info = api_request(
            module=self.module,
            endpoint="project/%s" % self.module.params["name"],
        )

        return resp

    def create_or_update_project(self):
        facts = self.get_project_facts()

        if facts is None:
            # If in check mode don't create project, simulate a fake project creation
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    before={},
                    after={
                        "name": self.module.params["name"]
                    },
                )

            resp, info = api_request(
                module=self.module,
                endpoint="projects",
                method="POST",
                data={
                    "name": self.module.params["name"],
                    "config": {},
                }
            )

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
                api_request(
                    module=self.module,
                    endpoint="project/%s" % self.module.params["name"],
                    method="DELETE",
                )

            self.module.exit_json(changed=True, before=facts, after={})


def main():
    # Also allow the user to set values for fetch_url
    argument_spec = api_argument_spec()
    argument_spec.update(dict(
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        name=dict(required=True, type='str'),
    ))

    argument_spec['api_token']['aliases'] = ['token']

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
