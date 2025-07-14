#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Florian Apolloner (@apollo13)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: consul_binding_rule
short_description: Manipulate Consul binding rules
version_added: 8.3.0
description:
  - Allows the addition, modification and deletion of binding rules in a Consul cluster using the agent. For more details
    on using and configuring binding rules, see U(https://developer.hashicorp.com/consul/api-docs/acl/binding-rules).
author:
  - Florian Apolloner (@apollo13)
extends_documentation_fragment:
  - community.general.consul
  - community.general.consul.actiongroup_consul
  - community.general.consul.token
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: partial
    details:
      - In check mode the diff misses operational attributes.
options:
  state:
    description:
      - Whether the binding rule should be present or absent.
    choices: ['present', 'absent']
    default: present
    type: str
  name:
    description:
      - Specifies a name for the binding rule.
      - 'Note: This is used to identify the binding rule. But since the API does not support a name, it is prefixed to the
        description.'
    type: str
    required: true
  description:
    description:
      - Free form human readable description of the binding rule.
    type: str
  auth_method:
    description:
      - The name of the auth method that this rule applies to.
    type: str
    required: true
  selector:
    description:
      - Specifies the expression used to match this rule against valid identities returned from an auth method validation.
      - If empty this binding rule matches all valid identities returned from the auth method.
    type: str
  bind_type:
    description:
      - Specifies the way the binding rule affects a token created at login.
    type: str
    choices: [service, node, role, templated-policy]
  bind_name:
    description:
      - The name to bind to a token at login-time.
      - What it binds to can be adjusted with different values of the O(bind_type) parameter.
    type: str
  bind_vars:
    description:
      - Specifies the templated policy variables when O(bind_type) is set to V(templated-policy).
    type: dict
"""

EXAMPLES = r"""
- name: Create a binding rule
  community.general.consul_binding_rule:
    name: my_name
    description: example rule
    auth_method: minikube
    bind_type: service
    bind_name: "{{ serviceaccount.name }}"
    token: "{{ consul_management_token }}"

- name: Remove a binding rule
  community.general.consul_binding_rule:
    name: my_name
    auth_method: minikube
    state: absent
"""

RETURN = r"""
binding_rule:
  description: The binding rule as returned by the Consul HTTP API.
  returned: always
  type: dict
  sample:
    Description: "my_name: example rule"
    AuthMethod: minikube
    Selector: serviceaccount.namespace==default
    BindType: service
    BindName: "{{ serviceaccount.name }}"
    CreateIndex: 30
    ID: 59c8a237-e481-4239-9202-45f117950c5f
    ModifyIndex: 33
operation:
  description: The operation performed.
  returned: changed
  type: str
  sample: update
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.consul import (
    AUTH_ARGUMENTS_SPEC,
    RequestError,
    _ConsulModule,
)


class ConsulBindingRuleModule(_ConsulModule):
    api_endpoint = "acl/binding-rule"
    result_key = "binding_rule"
    unique_identifiers = ["id"]

    def read_object(self):
        url = "acl/binding-rules?authmethod={0}".format(self.params["auth_method"])
        try:
            results = self.get(url)
            for result in results:
                if result.get("Description").startswith(
                    "{0}: ".format(self.params["name"])
                ):
                    return result
        except RequestError as e:
            if e.status == 404:
                return
            elif e.status == 403 and b"ACL not found" in e.response_data:
                return
            raise

    def module_to_obj(self, is_update):
        obj = super(ConsulBindingRuleModule, self).module_to_obj(is_update)
        del obj["Name"]
        return obj

    def prepare_object(self, existing, obj):
        final = super(ConsulBindingRuleModule, self).prepare_object(existing, obj)
        name = self.params["name"]
        description = final.pop("Description", "").split(": ", 1)[-1]
        final["Description"] = "{0}: {1}".format(name, description)
        return final


_ARGUMENT_SPEC = {
    "name": dict(type="str", required=True),
    "description": dict(type="str"),
    "auth_method": dict(type="str", required=True),
    "selector": dict(type="str"),
    "bind_type": dict(
        type="str", choices=["service", "node", "role", "templated-policy"]
    ),
    "bind_name": dict(type="str"),
    "bind_vars": dict(type="dict"),
    "state": dict(default="present", choices=["present", "absent"]),
}
_ARGUMENT_SPEC.update(AUTH_ARGUMENTS_SPEC)


def main():
    module = AnsibleModule(
        _ARGUMENT_SPEC,
        supports_check_mode=True,
    )
    consul_module = ConsulBindingRuleModule(module)
    consul_module.execute()


if __name__ == "__main__":
    main()
