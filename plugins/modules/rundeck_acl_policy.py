#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Loic Blot <loic.blot@unix-experience.fr>
# Sponsored by Infopro Digital. http://www.infopro-digital.com/
# Sponsored by E.T.A.I. http://www.etai.fr/
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: rundeck_acl_policy

short_description: Manage Rundeck ACL policies
description:
    - Create, update and remove Rundeck ACL policies through HTTP API.
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
    project:
        type: str
        description:
            - Sets the project which receive the ACL policy.
            - If unset, it's a system ACL policy.
    policy:
        type: str
        description:
            - Sets the ACL policy content.
            - ACL policy content is a YAML object as described in http://rundeck.org/docs/man5/aclpolicy.html.
            - It can be a YAML string or a pure Ansible inventory YAML object.
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
- name: Create or update a rundeck ACL policy in project Ansible
  community.general.rundeck_acl_policy:
    name: "Project_01"
    api_version: 18
    url: "https://rundeck.example.org"
    token: "mytoken"
    state: present
    project: "Ansible"
    policy:
      description: "my policy"
      context:
        application: rundeck
      for:
        project:
          - allow: read
      by:
        group: "build"

- name: Remove a rundeck system policy
  community.general.rundeck_acl_policy:
    name: "Project_01"
    url: "https://rundeck.example.org"
    token: "mytoken"
    state: absent
'''

RETURN = '''
rundeck_response:
    description: Rundeck response when a failure occurs.
    returned: failed
    type: str
before:
    description: Dictionary containing ACL policy information before modification.
    returned: success
    type: dict
after:
    description: Dictionary containing ACL policy information after modification.
    returned: success
    type: dict
'''

# import module snippets
import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.rundeck import (
    api_argument_spec,
    api_request,
)


class RundeckACLManager:
    def __init__(self, module):
        self.module = module

    def get_acl(self):
        resp, info = api_request(
            module=self.module,
            endpoint="system/acl/%s.aclpolicy" % self.module.params["name"],
        )

        return resp

    def create_or_update_acl(self):
        facts = self.get_acl()
        if facts is None:
            # If in check mode don't create project, simulate a fake project creation
            if self.module.check_mode:
                self.module.exit_json(changed=True, before={}, after=self.module.params["policy"])

            resp, info = api_request(
                module=self.module,
                endpoint="system/acl/%s.aclpolicy" % self.module.params["name"],
                method="POST",
                data={"contents": self.module.params["policy"]},
            )

            if info["status"] == 201:
                self.module.exit_json(changed=True, before={}, after=self.get_acl())
            elif info["status"] == 400:
                self.module.fail_json(msg="Unable to validate acl %s. Please ensure it's a valid ACL" %
                                          self.module.params["name"])
            elif info["status"] == 409:
                self.module.fail_json(msg="ACL %s already exists" % self.module.params["name"])
            else:
                self.module.fail_json(msg="Unhandled HTTP status %d, please report the bug" % info["status"],
                                      before={}, after=self.get_acl())
        else:
            if facts["contents"] == self.module.params["policy"]:
                self.module.exit_json(changed=False, before=facts, after=facts)

            if self.module.check_mode:
                self.module.exit_json(changed=True, before=facts, after=facts)

            resp, info = api_request(
                module=self.module,
                endpoint="system/acl/%s.aclpolicy" % self.module.params["name"],
                method="PUT",
                data={"contents": self.module.params["policy"]},
            )

            if info["status"] == 200:
                self.module.exit_json(changed=True, before=facts, after=self.get_acl())
            elif info["status"] == 400:
                self.module.fail_json(msg="Unable to validate acl %s. Please ensure it's a valid ACL" %
                                          self.module.params["name"])
            elif info["status"] == 404:
                self.module.fail_json(msg="ACL %s doesn't exists. Cannot update." % self.module.params["name"])

    def remove_acl(self):
        facts = self.get_acl()

        if facts is None:
            self.module.exit_json(changed=False, before={}, after={})
        else:
            # If not in check mode, remove the project
            if not self.module.check_mode:
                api_request(
                    module=self.module,
                    endpoint="system/acl/%s.aclpolicy" % self.module.params["name"],
                    method="DELETE",
                )

                self.module.exit_json(changed=True, before=facts, after={})


def main():
    # Also allow the user to set values for fetch_url
    argument_spec = api_argument_spec()
    argument_spec.update(dict(
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        name=dict(required=True, type='str'),
        policy=dict(type='str'),
        project=dict(type='str'),
    ))

    argument_spec['api_token']['aliases'] = ['token']

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ['state', 'present', ['policy']],
        ],
        supports_check_mode=True,
    )

    if not bool(re.match("[a-zA-Z0-9,.+_-]+", module.params["name"])):
        module.fail_json(msg="Name contains forbidden characters. The policy can contain the characters: a-zA-Z0-9,.+_-")

    if module.params["api_version"] < 14:
        module.fail_json(msg="API version should be at least 14")

    rundeck = RundeckACLManager(module)
    if module.params['state'] == 'present':
        rundeck.create_or_update_acl()
    elif module.params['state'] == 'absent':
        rundeck.remove_acl()


if __name__ == '__main__':
    main()
